r"""tools/patches/souls_quality.py - souls quality fixes (backlog #31).

RCA + evidence: docs/reports/souls_quality_audit.md (full-roster ground-truth
audit of the build40 GOLDEN arz, md5 b33c5a44) + docs/reports/souls_quality_fix.md.
This module fixes ALL FIVE granted-skill / augment tier inversions in the shipped
roster (a higher-rarity ring strictly WEAKER than a lower-rarity ring on the SAME
named skill) and the svc_uber per-tier icon law; FIX-WAVE-2 (2026-07-14) adds the
crowboar summoned-crow controller bug + the Tomb Guardian orphan-soul retirement,
and installs ROSTER-WIDE fail-loud verify() gates so none of these classes can
regress on any future build.

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
um_gustleech_28, chanceToEquipFinger2=66).

FIX (raise-only, preserves each soul's Normal anchor and its granted-skill NAME):
  bloodtip_soul_e itemSkillLevel 1 -> 7   => n/e/l = 5/7/9   (leech 30/42/46)
  gustleech_soul_e itemSkillLevel 4 -> 12
  gustleech_soul_l itemSkillLevel 7 -> 14 => n/e/l = 10/12/14 (leech 50/58/66)

PROVENANCE - RATIFIED BY WILL (2026-07-14, verbatim): "bloodtip 5/7/9 + gustleech
10/12/14 ship as-is". These two itemSkillLevel arrays are byte-identical to SV
0.98i, so the fix is a deliberate (amgoz1 data-entry-oversight) divergence from
SV-original data. The historical revert path is preserved below as the
`_SV_INVERSION_FIX` block - if SV's exact numbers are ever deemed sacrosanct here,
delete that block (the svc_uber trio + icon fixes stand independently). The
round-0 WILL-VETO flag is CLEARED (see docs/reports/souls_quality_fix.md).

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
FIX 4 (FIX-WAVE-2 D3, P1) - summon souls whose worn summon "resets before acting"
--------------------------------------------------------------------------------
Will (2026-07-14): "fix the crowboar soul's summoned crow bug ... sweep the roster
for any OTHER summon soul with the same broken on-attack+petLimit=1 shape and fix
those too (same bug = same wave)." Ground truth (SV098-authorship sweep over the
GOLDEN arz; regenerable by tools/debug/souls_quality_replay.py):

crowboar_soul_{n,e,l} grants the SHARED skill carrioncrow_summon.dbr (Skill_SpawnPet,
petLimit=10, petBurstSpawn=1, PERMANENT no-TTL, isPetDisplayable=0) via itemSkillName
WITH itemSkillAutoController = base_atenemy_onattack. So every wearer attack re-casts
Summon Carrion Crow; the flock re-bursts/resets before the crows can act. The mod's
PROVEN worn companion-summon convention is UNANIMOUS: Lyia Leafsong (summon_lyia,
petLimit 1, permanent, NO controller = manual-cast) and the 17 boss-summon souls -
cast once, the pet persists and fights.

BRIEF-vs-GROUND-TRUTH: Will's "petLimit=1" is a mental model of a single persistent
companion, NOT a DB value - NO on-attack summon ring in the roster is petLimit 1
(crowboar is 10; the siblings 3..10). The real signature is an on-attack-family
controller on a PERMANENT companion summon, at ANY petLimit.

FIX (remove itemSkillAutoController -> manual-cast, the Lyia model; ZERO shared-skill
collateral - we never touch the summon SKILLS the SV swarm souls share). SCOPE IS
ROSTER-DERIVED against the SV 0.98i design bible (upstream/soulvizier_098i), NOT a
namespace: a permanent-summon soul ring is fixed iff its on-attack controller was
introduced BY THE MOD - i.e. SV098 does NOT ship that same ring with an on-attack
controller (apply() + verify() both compute this; _summon_controller_fix_records).
Roster-wide sweep of the 76 permanent-summon rings carrying an on-attack controller:

* 52 rings / 18 families are amgoz1 SV-ORIGINALS shipped WITH the on-attack controller
  = deliberate "raise-a-swarm-as-you-attack" identities (direflock IS a flock; the
  skeleton-raisers raise skeletons; nebtaan/senusnet/menzus/bonelord/fenuku/frostmarrow/
  graklos/xiao/feira/aphiastas/dead-soldier+dead-archer raisers). SV = design bible ->
  LEFT UNTOUCHED and flagged for Will as a design decision, NOT a defect (report 3.5).
  Correct obtainability (contra a prior "most drop-gated" claim): direflock/nebtaan/
  senusnet/menzus/bonelord/fenuku/frostmarrow/graklos drop from obtainable Heroes at 66,
  xiao from a Boss at 25; the rest are gated.

* 24 rings / 8 families carry a MOD-INTRODUCED on-attack controller and ARE fixed:
    Category A - MOD-ONLY svc_uber (no SV original; mod-generated deviants of the
      unanimous manual-cast convention; Will named crowboar):
        crowboar    carrioncrow_summon  petLimit 10  base_atenemy_onattack
        glittertail summon_firesprite   petLimit 5   awakeneddeadsoul_onattack
        koroush     wraith_summon       petLimit 5   base_atenemy_onattack
        nkac        skeleton_summon     petLimit 5   base_atenemy_onattack
    Category B - SV-ORIGINAL ring the MOD gave an on-attack controller SV never shipped
      (removing it RESTORES amgoz's manual-cast design):
        komara / melalos / oythroneus  summon_zombiesoldier  petLimit 6  base_atenemy_onattack
          (the monolith's generic _AC_ON_ATTACK on a SUMMON; SV098 shipped all three
           manual-cast). komara (um_komara_38, Hero 66) + melalos (um_melalos_19, Boss 66)
           are OBTAINABLE - the exact same-bug obtainable rings a prior svc_uber-only
           scope MISSED (the round-1 vet HIGH); oythroneus is currently drop-gated.
        carrionlord  carrioncrow_summon  petLimit 10  (RESOLVED - see below)
          - REASSIGNED to Summon Carrion Crow by skill_quality (REASSIGN
            'toxeus_flashpowder.dbr' tagSoulName49). RESOLVED (lowlift wave item 5,
            2026-07-15): skill_quality's REASSIGN entry previously set ON_ATTACK, which
            souls_quality (registry pos 13, after skill_quality's pos 4) then stripped
            again as a mod-introduced controller on a permanent summon - a documented
            but confusing later-wins collision (the FINAL db was already correct;
            only the intermediate state and the code's own honesty about it were not).
            Ground-truthed: carrionlord is a mod REASSIGN target (Track B, off-theme
            toxeus_flashpowder -> its own identity-true crow-summon), NOT one of the 18
            amgoz1 SV-ORIGINAL on-attack swarm souls above - there is no upstream design
            to defer to, so the class-wide manual-cast convention applies cleanly, same
            as crowboar/glittertail/koroush/nkac/komara/melalos/oythroneus. skill_quality
            now sets controller=None directly (tools/patches/skill_quality.py, REASSIGN
            'toxeus_flashpowder.dbr' tagSoulName49) - BOTH modules agree at the source,
            no collision, no S4b WARN, and the FINAL db is byte-identical to before this
            reconciliation (souls_quality's roster-derived sweep simply finds nothing
            left to remove for this ring - a harmless no-op, not a functional change).

Root cause (documented follow-ups for those lanes; NOT rewritten here to keep this a
disjoint soul-ring patch): apply_svc_patches reuses _AC_ON_ATTACK for summon-granting
souls (right for on-attack PROCS like Ground Smash, wrong for summons), and
skill_quality REASSIGN applies ON_ATTACK generically incl. the carrionlord summon.

Pet.tpl safety: touches ONLY the item ring's controller field - no pet record, no
Monster.tpl->Pet.tpl copy, no spawnObjectsTimeToLive change; the pets are already valid
Pet.tpl aggressive friendlies. validate_summon_pets stays PASS. Known minor residual
(NOT the reported bug): carrioncrow_summon ships isPetDisplayable=0, so the manual-cast
crow fights but shows no pet-window bar - a shared-skill content-pass item, unchanged.
A future intentional mod on-attack swarm goes in _SUMMON_CONTROLLER_WAIVER (fail-loud
forces the decision to be explicit).

--------------------------------------------------------------------------------
FIX 5 (FIX-WAVE-2 D2) - Tomb Guardian orphan-soul retirement
--------------------------------------------------------------------------------
Will (2026-07-14): "Do not promote tomb guardian and do not have him drop a soul."
Ground truth (gt_probe): um_tombguardian_26 = monsterClassification Common (a
genuine 609-HP Anubis Hound; its Hero cousin um_foulbeast_28 has 5612 HP), yet
apply_svc_patches._place_orphan_monsters wires it - "against the Hero/Boss/Quest
design" (its own comment) - to svc_uber\um_tombguardian_soul via lootFinger2Item1,
then _gate_common_soul_leaks force-zeroes chanceToEquipFinger2 to 0.0. Net today:
the soul is REFERENCED (loot table) but UNOBTAINABLE (chance 0) - the exact
"referenced-but-unobtainable" ghost the directive flags. The only reference to
um_tombguardian_soul anywhere in the DB is this one monster (verified whole-DB
scan). No enchanting formula uses it. There is no other natural Hero/Boss Anubis
Hound to carry it without promoting the guardian (barred).

FIX (keep Common; do not drop; retire the soul cleanly with its tag):
  (a) DETACH: clear um_tombguardian_26.lootFinger2Item1 (the 3 soul refs) so the
      soul is no longer attached to any loot path (chanceToEquipFinger2 already 0;
      classification stays Common). This also removes what would become a dangling
      loot ref once the soul records are gone.
  (b) RETIRE: remove the now-unreferenced um_tombguardian_soul_{n,e,l} records.
  (c) TAG: drop tagSVCSoulTombguardian from the tags dict so Text.arc carries no
      dangling name (the 3 removed rings were its only referents).
Guarded/idempotent: if a future root-cause change (make _place_orphan_monsters
skip soul creation for deny-listed records) removes the soul upstream, every step
here no-ops cleanly.

--------------------------------------------------------------------------------
NOT fixed here (see the report's FIX-LIST + WILL-DECISION sections)
--------------------------------------------------------------------------------
* P2-c boss-summon nymph icons (17 souls): fixed on the unmerged
  feat/b40-soul-icons branch (commit 9db3f5f) - VERIFIED it merges CLEANLY onto
  current main (merge-tree, 0 conflicts), so it is a REQUIRED member of the
  integration merge set (no duplicate work here; it edits apply_svc_patches.py,
  disjoint from this module and from the FIX 4 summon souls).
* P2-d Soulfeeder pet spirit-breath: verified an AUDIT FALSE POSITIVE - the mod's
  bonepet20 already casts bonescourge_spiritbreath. Nothing to restore.
* 52 amgoz1 SV-original on-attack SWARM souls (direflock, the skeleton/dead-raisers,
  nebtaan, senusnet, menzus, bonelord, fenuku, frostmarrow, graklos, xiao, feira,
  aphiastas, ...): amgoz1 shipped these WITH the on-attack controller = deliberate
  design (SV = the design bible). LEFT UNTOUCHED and flagged for Will (report 3.5).
* P3-a 79 SV drop-gated souls / P3-b 5 formula-only souls / P3-c SV pet-equip
  dangles / P3-d SV DB hygiene: SUBJECTIVE / design decisions for Will, left
  documented untouched (souls_quality_audit.md sec 5). These carry correct data
  under the deliberate Hero/Boss/Quest drop law - not blatant errors.

Module contract (tools/patches/README.md): MODULE_NAME + apply(db, tags), plus a
post-finalization verify(db, tags) that fail-louds the tier-monotonicity (roster-
wide), the svc_uber icon law, the ROSTER-WIDE no-mod-introduced-on-attack-controller
law for permanent companion summons (judged vs the SV098 design bible), and the Tomb
Guardian retirement, over the FINAL assembled db so none of these classes can
silently regress.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # tools/ on path

MODULE_NAME = ('Souls quality (roster tier inversion x5 + svc_uber per-tier icons '
               '+ crow-summon manual-cast + tombguardian retire)')

_SOUL_PREFIX = r'records\item\equipmentring\soul' + '\\'
_UBER = '\\soul\\svc_uber\\'


def _norm(p):
    return str(p).replace('/', '\\').lower().strip()


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
# RATIFIED by Will 2026-07-14 (bloodtip 5/7/9, gustleech 10/12/14). This block is
# also the documented HISTORICAL REVERT PATH: deleting it reverts to SV's exact
# byte-identical itemSkillLevel arrays (the svc_uber trio + icons stand alone).
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

# ── FIX 4 (D3): mod-introduced on-attack controllers on PERMANENT companion-summon
# soul rings (the "resets before acting" bug). The fix set is ROSTER-DERIVED against
# the SV 0.98i design bible - NOT a hardcoded family list - so a future mod-added
# controller is caught by the same predicate (apply() removes it, verify() fail-louds).
# A ring is fixed iff it grants a PERMANENT (no-TTL) Skill_SpawnPet AND carries an
# on-attack-family controller AND that controller was NOT shipped by amgoz1 (SV098
# does NOT ship the SAME ring path with an on-attack controller). See _summon_controller_fix_records.

# On-attack-family controllers fire when the WEARER attacks (the re-summon bug).
# 'onattacked'/'lowhealth' (when the wearer IS attacked / is hurt) are REACTIVE, not
# the bug, and are deliberately excluded. Curated known set + a suffix heuristic so a
# novel offensive-trigger template is still recognised (future-proofing the gate).
_KNOWN_ONATTACK_CTL = frozenset([
    'base_atenemy_onattack.dbr', 'base_atself_onattack.dbr', 'base_atself_onmeleehit.dbr',
    'base_atself_onrangedhit.dbr', 'poisonbomb_onattack.dbr', 'awakeneddeadsoul_onattack.dbr',
    'asorissoul_onmeleehit.dbr', 'bonelordsoul_onattack.dbr', 'monolithessence_onattack.dbr',
])

# Intentional-design escape hatch: exact ring paths (normalized) that MAY keep a
# mod-authored on-attack summon controller as a deliberate design. EMPTY today (all 8
# mod-introduced families, INCLUDING carrionlord - RESOLVED lowlift wave item 5, see
# the class-sweep comment above - are genuine bugs per Will + the manual-cast
# convention, not deliberate swarm identities). A future intentional mod on-attack
# swarm goes here (add its tier paths; verify() then stops flagging it). Kept
# explicit so the decision is never silent.
_SUMMON_CONTROLLER_WAIVER = frozenset()

# SV 0.98i design-bible arz (the authorship oracle). Resolved lazily at apply()/verify()
# time (never at import, so _check_registry stays cheap) and cached module-wide.
_SV098_REL = os.path.join('upstream', 'soulvizier_098i', 'Database', 'database.arz')
_sv098_cache = {}

# ── FIX 5 (D2): Tomb Guardian orphan-soul retirement ────────────────────────
_TG_MONSTER = r'records\creature\monster\tombguardian\um_tombguardian_26.dbr'
_TG_LOOT_FIELD = 'lootFinger2Item1'
_TG_SOULS = [r'records\item\equipmentring\soul\svc_uber\um_tombguardian_soul_%s.dbr' % t
             for t in 'nel']
_TG_TAG = 'tagSVCSoulTombguardian'


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


def _field_key(db, rec, field):
    """Return the stored field key (handles the '<field>###<suffix>' form) or None."""
    fields = db.get_fields(rec)
    if not fields:
        return None
    for k in fields:
        if k == field or k.split('###')[0] == field:
            return k
    return None


def _remove_field(db, rec, field):
    """Delete a field from a record in place (like Lyia, which has NO
    itemSkillAutoController). Returns True if a field was removed."""
    fields = db.get_fields(rec)
    if not fields:
        return False
    key = _field_key(db, rec, field)
    if key is None:
        return False
    del fields[key]
    db._modified.add(rec)
    return True


def _remove_record(db, exact_name):
    """Fully retire a record from the db (all internal maps). Returns True if it
    existed. write_arz iterates db._raw_records, so popping it there removes it
    from the built arz."""
    existed = exact_name in db._raw_records
    db._raw_records.pop(exact_name, None)
    db._decoded_cache.pop(exact_name, None)
    db._record_types.pop(exact_name, None)
    db._record_timestamps.pop(exact_name, None)
    db._modified.discard(exact_name)
    return existed


def _grants_permanent_summon(db, nm, rec):
    """True iff the ring's itemSkillName resolves (in db) to a PERMANENT (no
    spawnObjectsTimeToLive) Skill_SpawnPet. This is the worn companion-summon shape
    (Lyia / crowboar); a TTL'd summon is a temporary proc, not a companion, and is
    out of scope."""
    isn = _sval(db, rec, 'itemSkillName')
    if not isn:
        return False
    sk = nm.get(_norm(isn))
    if sk is None or _sval(db, sk, 'Class') != 'Skill_SpawnPet':
        return False
    ttl = db.get_field_value(sk, 'spawnObjectsTimeToLive')
    ttl_list = ttl if isinstance(ttl, list) else ([ttl] if ttl not in (None, '') else [])
    return not ttl_list


def _ctl_base(db, rec):
    """Basename (normalized) of the ring's itemSkillAutoController, or None."""
    c = _sval(db, rec, 'itemSkillAutoController')
    return _norm(c).rsplit('\\', 1)[-1] if c else None


def _is_on_attack_controller(base):
    """True iff a controller basename is an OFFENSIVE on-attack-family trigger (fires
    when the wearer attacks) - the re-summon defect signature. Curated known set plus
    a suffix heuristic; 'onattacked' (wearer IS attacked) and 'lowhealth' are REACTIVE
    and excluded."""
    if not base:
        return False
    b = base.lower()
    if b in _KNOWN_ONATTACK_CTL:
        return True
    if 'onattacked' in b:
        return False
    return ('onattack' in b) or ('onmeleehit' in b) or ('onrangedhit' in b) or ('onanyhit' in b)


def _load_sv098():
    """Load + cache the pristine SV 0.98i design-bible arz (authorship oracle for the
    summon-controller fix set). Resolution order: env SVC_SV098_ARZ, else the canonical
    upstream/ path walking UP from this module's dir and from cwd (so it resolves from a
    linked worktree whose own upstream/ is unpopulated). Fail-loud if absent - SV098 is
    a required build input (build_svc_database takes it as argv), so this never silently
    skips the roster-wide gate."""
    if 'db' in _sv098_cache:
        return _sv098_cache['db'], _sv098_cache['nm']
    from arz_patcher import ArzDatabase
    cand = None
    env = os.environ.get('SVC_SV098_ARZ')
    if env and os.path.isfile(env):
        cand = env
    else:
        for base in (Path(__file__).resolve().parent, Path.cwd().resolve()):
            d = base
            for _ in range(10):
                p = d / _SV098_REL
                if p.is_file():
                    cand = str(p)
                    break
                if d.parent == d:
                    break
                d = d.parent
            if cand:
                break
    if cand is None:
        raise SystemExit(
            "souls_quality: cannot locate the SV 0.98i design-bible arz (%s) - needed to "
            "roster-derive the mod-introduced on-attack summon-controller fix set. Set "
            "SVC_SV098_ARZ or run from the repo tree." % _SV098_REL)
    sdb = ArzDatabase.from_arz(Path(cand))
    snm = {_norm(x): x for x in sdb.record_names()}
    _sv098_cache['db'] = sdb
    _sv098_cache['nm'] = snm
    _sv098_cache['path'] = cand
    return sdb, snm


def _sv_has_onattack_summon(sv_db, sv_nm, norm_ring):
    """True iff SV 0.98i ships THIS ring path WITH an on-attack controller = amgoz1's
    deliberate on-attack swarm design (leave it). False if SV lacks the ring (mod-only)
    or ships it without an on-attack controller (mod added one)."""
    sv = sv_nm.get(norm_ring)
    if sv is None:
        return False
    return _is_on_attack_controller(_ctl_base(sv_db, sv))


def _summon_controller_fix_records(db, nm=None):
    """ROSTER-DERIVED fix set: every soul equipmentring path whose on-attack summon
    controller was introduced BY THE MOD. A ring qualifies iff it grants a PERMANENT
    Skill_SpawnPet AND carries an on-attack-family controller AND is not waived AND
    amgoz1 did NOT ship that same ring with an on-attack controller (SV098 oracle).
    Used identically by apply() (records to fix) and verify() (must be empty post-fix),
    so the two can never drift. Returns a set of exact record names."""
    nm = nm if nm is not None else _name_map(db)
    sv_db, sv_nm = _load_sv098()
    out = set()
    for rec, nn, tier in _iter_soul_rings(db, nm):
        if nn in _SUMMON_CONTROLLER_WAIVER:
            continue
        if not _is_on_attack_controller(_ctl_base(db, rec)):
            continue
        if not _grants_permanent_summon(db, nm, rec):
            continue
        if _sv_has_onattack_summon(sv_db, sv_nm, nn):
            continue  # amgoz1 designed this on-attack swarm - leave it
        out.add(rec)
    return out


def apply(db, tags):
    nm = _name_map(db)

    # ── FIX 5 (D2): Tomb Guardian orphan-soul retirement (FIRST, so the icon/level
    #    passes below never touch the to-be-removed tombguardian rings) ──────────
    tg = nm.get(_norm(_TG_MONSTER))
    tg_detached = tg_removed = 0
    if tg is not None:
        # (a) detach: clear the soul refs from the loot slot (keep the 3-difficulty
        #     arity as empty strings; chanceToEquipFinger2 is already 0.0 and the
        #     Common classification is left untouched, both per Will's directive).
        cur = db.get_field_value(tg, _TG_LOOT_FIELD)
        cur_list = cur if isinstance(cur, list) else ([cur] if cur is not None else [])
        if any(isinstance(v, str) and 'um_tombguardian_soul' in v.lower() for v in cur_list):
            db.set_field(tg, _TG_LOOT_FIELD, [''] * (len(cur_list) or 3))
            tg_detached = 1
    # (b) retire the now-unreferenced soul records
    for sp in _TG_SOULS:
        ex = nm.get(_norm(sp))
        if ex is not None and _remove_record(db, ex):
            tg_removed += 1
            nm.pop(_norm(sp), None)
    # (c) drop the dangling name tag (no-op in the replay's empty tags dict)
    tg_tag_dropped = 0
    if isinstance(tags, dict) and _TG_TAG in tags:
        del tags[_TG_TAG]
        tg_tag_dropped = 1

    # ── FIX 4 (D3): remove the MOD-INTRODUCED on-attack controller from every
    #    permanent companion-summon ring -> manual-cast (the Lyia convention). The
    #    set is roster-derived vs the SV098 design bible (Category A mod-only svc_uber
    #    + Category B SV-original rings the mod gave a controller SV never shipped),
    #    so amgoz1's designed on-attack swarms are left untouched. ─────────────────
    ctl_removed = 0
    for rec in _summon_controller_fix_records(db, nm):
        if _remove_field(db, rec, 'itemSkillAutoController'):
            ctl_removed += 1

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

    print("    souls_quality: raised %d tier-inversion level(s) (crowboar/onyxspine/"
          "steamcrawler/bloodtip/gustleech); fixed %d svc_uber e/l tier-icon(s); "
          "removed %d mod-introduced on-attack summon-controller(s) [SV098-derived, "
          "8 families A+B]; tombguardian detached=%d retired=%d/3 tag_dropped=%d"
          % (lvl_edits, icon_edits, ctl_removed, tg_detached, tg_removed, tg_tag_dropped))


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


def _crow_controller_violations(db, nm=None):
    """ROSTER-WIDE (every soul equipmentring, NOT just svc_uber): no soul ring may
    carry a MOD-INTRODUCED on-attack controller on a PERMANENT companion summon. The
    residual set is the SAME roster-derived predicate apply() removes
    (_summon_controller_fix_records: permanent SpawnPet + on-attack controller + not
    amgoz-designed vs the SV098 bible + not waived), so post-fix it MUST be empty. A
    ring amgoz1 shipped with an on-attack controller (its designed swarm) is NOT a
    violation. Returns [(record, controller)] for anything still mod-broken."""
    nm = nm if nm is not None else _name_map(db)
    bad = []
    for rec in _summon_controller_fix_records(db, nm):
        bad.append((rec, _sval(db, rec, 'itemSkillAutoController') or '?'))
    return bad


def _tombguardian_violations(db, nm=None):
    """Tomb Guardian retirement holds: um_tombguardian_26 (if present) carries NO
    um_tombguardian_soul reference in any loot field, and none of the 3
    um_tombguardian_soul_{n,e,l} records exist. Returns a list of violation strings."""
    nm = nm if nm is not None else _name_map(db)
    bad = []
    tg = nm.get(_norm(_TG_MONSTER))
    if tg is not None:
        fields = db.get_fields(tg) or {}
        for k, tf in fields.items():
            for v in tf.values:
                if isinstance(v, str) and 'um_tombguardian_soul' in v.lower():
                    bad.append("um_tombguardian_26 still references the soul via %s: %s"
                               % (k.split('###')[0], v))
    for sp in _TG_SOULS:
        if _norm(sp) in nm:
            bad.append("retired soul record still present: %s" % sp)
    return bad


def verify(db, tags):
    """POST-FINALIZATION fail-loud gates (run over the FINAL assembled db, after
    run_registry_gates' backstop + drop forcer). Proves the tier-inversion class
    holds roster-wide, the per-tier icon law holds across svc_uber, the ROSTER-WIDE
    manual-cast summon law holds (no MOD-INTRODUCED on-attack controller on any
    permanent companion summon, judged vs the SV098 design bible - so amgoz's designed
    swarms are allowed but a new mod-added controller on ANY soul, svc_uber or not,
    fail-louds), and the Tomb Guardian soul is fully retired - none can silently regress."""
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

    crow = _crow_controller_violations(db, nm)
    if crow:
        lines = '\n'.join("      %s auto-casts its permanent summon on attack (%s)"
                          % (r.rsplit('\\', 1)[-1], c.rsplit('\\', 1)[-1]) for r, c in crow)
        raise SystemExit(
            "souls_quality verify: %d companion-summon ring(s) carry a MOD-INTRODUCED "
            "on-attack controller (crow-reset bug - must be manual-cast per the Lyia "
            "convention; if an intentional amgoz-style on-attack swarm, add to "
            "_SUMMON_CONTROLLER_WAIVER):\n%s" % (len(crow), lines))

    tgbad = _tombguardian_violations(db, nm)
    if tgbad:
        raise SystemExit(
            "souls_quality verify: Tomb Guardian retirement incomplete:\n      "
            + "\n      ".join(tgbad))

    print("    souls_quality verify OK: roster tiers monotonic (n<=e<=l) across "
          "every soul family + per-tier svc_uber icons correct + roster-wide "
          "companion summons manual-cast (no mod-introduced on-attack re-summon, "
          "SV098-derived) + tombguardian soul retired")
