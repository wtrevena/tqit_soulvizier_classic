r"""tools/patches/souls_quality.py - souls quality fixes (backlog #31).

RCA + evidence: docs/reports/souls_quality_audit.md (full-roster ground-truth
audit of the build40 GOLDEN arz, md5 b33c5a44) + docs/reports/souls_quality_fix.md.
This module fixes ALL FIVE granted-skill / augment tier inversions in the shipped
roster (a higher-rarity ring strictly WEAKER than a lower-rarity ring on the SAME
named skill) and the svc_uber per-tier icon law, and installs a ROSTER-WIDE
fail-loud verify() so the inversion class cannot regress on any future build.

The five inverted families (roster-wide monotonicity scan of the GOLDEN arz -
tools/debug/souls_quality_replay.py reproduces it):

  svc_uber\crowboar_soul       aug1/aug2 + itemSkillLevel  n/e/l = 1/2/1   (mod-generated)
  svc_uber\onyxspine_soul      aug1/aug2                   n/e/l = 1/2/1   (mod-generated)
  svc_uber\steamcrawler_soul   aug1/aug2                   n/e/l = 1/2/1   (mod-generated)
  spider\bloodtip_soul         itemSkillLevel (Devour)     n/e/l = 5/1/9   (SV-inherited)
  vulture\gustleech_soul       itemSkillLevel (Leechstrike) n/e/l = 10/4/7 (SV-inherited)

--------------------------------------------------------------------------------
FIX 1 (P1, the 3 mod-generated svc_uber souls) - Legendary WEAKER than Epic
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
FIX 2 (round-2, P1, the 2 SV-inherited souls) - grant WEAKER at higher rarity
--------------------------------------------------------------------------------
bloodtip_soul grants records\skills\soulskills\bloodtip_devour.dbr (a per-level-
scaled lifeleech Skill_AttackRadius, skillMaxLevel 20) at itemSkillLevel n/e/l =
5/1/9: the Epic ring grants Devour at level 1 (leech-min 14), STRICTLY WEAKER than
the Normal ring's level 5 (leech-min 30). gustleech_soul grants
records\skills\sv\gustleech\leechstrike_soul.dbr (per-level Skill_AttackWeapon,
maxLevel 20) at itemSkillLevel n/e/l = 10/4/7: BOTH the Epic (level 4, leech-min
26) and the Legendary (level 7, leech-min 38) are weaker than the Normal (level
10, leech-min 50). Both are obtainable Hero souls (um_bloodtip_18 /
um_gustleech_28, chanceToEquipFinger2=66) - a farmed Epic/Legendary that is
strictly worse than the common Normal (the exact 'DONE means DONE' repeat-report
shape).

PROVENANCE (flagged for Will, see report WILL VETO): these two itemSkillLevel
arrays are BYTE-IDENTICAL to SV 0.98i (upstream/soulvizier_098i). They are judged
amgoz1 DATA-ENTRY OVERSIGHTS, not intent: every OTHER field on both rings tiers
UPWARD n->e->l correctly (bloodtip characterLife 120/218/318, its own leech
20/34/50; gustleech deflect 5/7/9, offensiveLifeMin 12/21/29) - no designer
scales 8 base stats upward per tier and then makes the granted skill weaker on
the better ring. Fixing them is a deliberate divergence from SV-original data.

FIX (raise-only, preserves each soul's Normal anchor and its granted-skill NAME):
  bloodtip_soul_e itemSkillLevel 1 -> 7   => n/e/l = 5/7/9   (leech 30/42/46)
  gustleech_soul_e itemSkillLevel 4 -> 12
  gustleech_soul_l itemSkillLevel 7 -> 14 => n/e/l = 10/12/14 (leech 50/58/66)
Both targets stay well within the skills' skillMaxLevel (20). Raise-only means no
player loses power vs the current shipped ring; the fix only lifts the two
under-levelled tiers above the tier below them.

--------------------------------------------------------------------------------
FIX 3 (P2-b, 54 families / 108 rings) - Epic + Legendary show the Normal icon
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
post-finalization verify(db, tags) that fail-louds the tier-monotonicity (roster-
wide, EVERY soul equipmentring family) + svc_uber icon invariants over the FINAL
assembled db so the class cannot silently regress.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

MODULE_NAME = 'Souls quality (roster tier inversion x5 + svc_uber per-tier icons)'

_SOUL_PREFIX = r'records\item\equipmentring\soul' + '\\'
_UBER = '\\soul\\svc_uber\\'

# FIX 1: the 3 mod-generated svc_uber DEFICIENT souls - exact L-tier target
# levels (audit sec 4). Values match the healthy bloodrunner/xix Legendary tier
# (3). We only RAISE.
_DEFICIENT_L_FIX = {
    r'records\item\equipmentring\soul\svc_uber\crowboar_soul_l.dbr':
        {'augmentSkillLevel1': 3, 'augmentSkillLevel2': 3, 'itemSkillLevel': 3},
    r'records\item\equipmentring\soul\svc_uber\onyxspine_soul_l.dbr':
        {'augmentSkillLevel1': 3, 'augmentSkillLevel2': 3},
    r'records\item\equipmentring\soul\svc_uber\steamcrawler_soul_l.dbr':
        {'augmentSkillLevel1': 3, 'augmentSkillLevel2': 3},
}

# FIX 2 (round-2): the 2 SV-inherited souls whose GRANT is weaker at a higher
# rarity. Raise-only, preserves the granted-skill NAME + the Normal anchor.
# These itemSkillLevel arrays are byte-identical to SV 0.98i -> a deliberate
# divergence from SV-original data, flagged in the report WILL VETO section.
_SV_INVERSION_FIX = {
    # bloodtip 5/1/9 -> 5/7/9 : only the Epic ring is under-levelled.
    r'records\item\equipmentring\soul\spider\bloodtip_soul_e.dbr':
        {'itemSkillLevel': 7},
    # gustleech 10/4/7 -> 10/12/14 : both Epic and Legendary are under-levelled.
    r'records\item\equipmentring\soul\vulture\gustleech_soul_e.dbr':
        {'itemSkillLevel': 12},
    r'records\item\equipmentring\soul\vulture\gustleech_soul_l.dbr':
        {'itemSkillLevel': 14},
}

# All raise-only level edits, keyed by exact record path.
_LEVEL_FIX = dict(_DEFICIENT_L_FIX)
_LEVEL_FIX.update(_SV_INVERSION_FIX)

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
    m = re.search(r'_([nel])\.dbr$', norm_name)
    return m.group(1) if m else None


def _is_soul_ring(db, rec):
    """A soul equipmentring record (ArmorJewelry_Ring class or jewelry_ring
    template). Matches the audit's ring enumeration so verify() reasons over the
    same 857 tier-families the ground-truth scan did (excludes soultemplate/other
    non-ring records that live under the soul prefix)."""
    cls = _sval(db, rec, 'Class')
    if cls == 'ArmorJewelry_Ring':
        return True
    tpl = _norm(_sval(db, rec, 'templateName') or '')
    return tpl.endswith('jewelry_ring.tpl')


def _iter_soul_rings(db, nm=None):
    """(exact_name, norm_name, tier) for EVERY soul equipmentring ring with an
    n/e/l tier suffix (roster-wide, not just svc_uber)."""
    names = nm.values() if nm is not None else db.record_names()
    for n in names:
        nn = _norm(n)
        if not nn.startswith(_SOUL_PREFIX) or not nn.endswith('.dbr'):
            continue
        tier = _tier_of(nn)
        if tier and _is_soul_ring(db, n):
            yield n, nn, tier


def _iter_uber_rings(db, nm=None):
    """(exact_name, norm_name, tier) for every svc_uber soul ring with an n/e/l tier."""
    for n, nn, tier in _iter_soul_rings(db, nm):
        if _UBER in nn:
            yield n, nn, tier


def _family_key(norm_name):
    """dir\\<base minus _tier> - the tier-family key (e.g. spider\\bloodtip_soul)."""
    rel = norm_name[len(_SOUL_PREFIX):]
    base = rel.rsplit('\\', 1)[-1]
    fam_dir = rel.rsplit('\\', 1)[0] if '\\' in rel else ''
    m = re.match(r'^(.*?)_([nel])\.dbr$', base)
    stem = m.group(1) if m else (base[:-4] if base.endswith('.dbr') else base)
    return (fam_dir + '\\' + stem) if fam_dir else stem


def apply(db, tags):
    nm = _name_map(db)

    # ── FIX 1 + FIX 2: tier-level inversions (raise-only, clobber-safe) ─────────
    lvl_edits = 0
    for path, fields in _LEVEL_FIX.items():
        rec = nm.get(_norm(path))
        if rec is None:
            raise SystemExit(
                "souls_quality: inversion-fix target absent from db: %s (build "
                "base changed - refusing to run silently)" % path)
        for field, target in fields.items():
            cur = _ival(db, rec, field)
            if cur is None:
                # The field must exist (augment/grant already authored) so
                # set_field preserves its INT dtype. A missing field would mean
                # the soul shape changed under us - fail loud rather than guess.
                raise SystemExit(
                    "souls_quality: %s missing field %s (expected authored "
                    "upstream) - shape changed" % (path, field))
            if cur < target:
                # Field exists -> no explicit dtype (INT preserved; the
                # cloned-record dtype-corruption law is about NEW fields).
                db.set_field(rec, field, target)
                lvl_edits += 1

    # ── FIX 3: per-tier soul icons on svc_uber e/l rings ───────────────────────
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

    print("    souls_quality: raised %d tier-inversion level(s) (crowboar/"
          "onyxspine/steamcrawler/bloodtip/gustleech); fixed %d svc_uber e/l "
          "tier-icon(s)" % (lvl_edits, icon_edits))


def _monotonicity_violations(db, nm=None):
    """ROSTER-WIDE: every soul equipmentring family with all 3 tiers must have
    non-decreasing (n<=e<=l) levels on each augmentSkillLevel1..4 whose augment
    NAME is present AND IDENTICAL in all 3 tiers, and on itemSkillLevel where the
    granted skill NAME is present AND IDENTICAL in all 3 tiers.

    The same-NAME guard is load-bearing: a family whose Epic ring grants a
    DIFFERENT skill than its Normal ring is not an inversion of one skill, so its
    levels are not comparable (comparing them would false-positive the build gate
    on a legitimate design). Returns [(family, field, [n,e,l])]."""
    nm = nm if nm is not None else _name_map(db)
    fam = {}
    for rec, nn, tier in _iter_soul_rings(db, nm):
        fam.setdefault(_family_key(nn), {})[tier] = rec
    bad = []
    for clean, tiers in sorted(fam.items()):
        if not all(t in tiers for t in ('n', 'e', 'l')):
            continue
        recs = [tiers['n'], tiers['e'], tiers['l']]
        for k in (1, 2, 3, 4):
            names = [_norm(_sval(db, r, 'augmentSkillName%d' % k) or '') for r in recs]
            if not all(names) or len(set(names)) != 1:
                continue  # slot absent in a tier, or a different augment per tier
            lv = [_ival(db, r, 'augmentSkillLevel%d' % k) for r in recs]
            if None not in lv and not (lv[0] <= lv[1] <= lv[2]):
                bad.append((clean, 'augmentSkillLevel%d' % k, lv))
        isn = [_norm(_sval(db, r, 'itemSkillName') or '') for r in recs]
        if all(isn) and len(set(isn)) == 1:
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
    holds across the WHOLE soul roster (every equipmentring family, not just
    svc_uber) and the per-tier icon law holds across svc_uber, so neither class
    can silently regress in a future content build."""
    nm = _name_map(db)

    mono = _monotonicity_violations(db, nm)
    if mono:
        lines = '\n'.join("      %s %s n/e/l=%s" % (c, f, lv) for c, f, lv in mono)
        raise SystemExit(
            "souls_quality verify: soul augment/grant tier INVERSION "
            "(higher rarity weaker than lower) on %d field(s):\n%s"
            % (len(mono), lines))

    icons = _icon_violations(db, nm)
    if icons:
        lines = '\n'.join("      %s (tier %s) has %s"
                          % (r.rsplit('\\', 1)[-1], t, b) for r, t, b in icons)
        raise SystemExit(
            "souls_quality verify: %d svc_uber ring(s) show a wrong-tier soul "
            "icon:\n%s" % (len(icons), lines))

    print("    souls_quality verify OK: roster tiers monotonic (n<=e<=l) across "
          "every soul family + per-tier svc_uber icons correct")
