r"""svc_chest_artifacts.py - "ARTIFACTS SHOULD NEVER DROP FROM CHESTS" (Will 2026-08-11).

WILL, VERBATIM (2026-08-11): "artifacts should never drop from chests".

THE PREMISE THIS RULING ARRIVED WITH WAS WRONG, AND THAT IS THE FIRST THING TO SAY
----------------------------------------------------------------------------------
The ruling was relayed as a no-op - "current state already complies (0/292); assert it
with a fail-loud gate so it can never regress". It does not comply. MEASURED on the
shipped b83 arz `44499f56`, which is live on Steam and on DEV right now:

    30 of the 57 mod loot surfaces reach an ItemArtifact record.
    16 distinct artifacts are reachable: 6 equippable + 10 mercenary scrolls.

The six are the IT "divine artifacts" - Ikon of Zeus, Thoth's Glory, Marduk's Tablet of
Destiny, Golden Eye of Sun Wukong, Crescent Moon of Artemis, Demeter's Bounty - and they
are reachable BY DESIGN, from `svc_craft_reagents_artifact_l01` into `04_l_misc`. That
row is R-185, a Will ruling of 2026-08-10 whose own rule G1 requires every non-green
reagent of every uber craftable to be findable in a Legendary chest. Two craftables
(Mortok's Skull, The All-Seeing Eye) name nothing but divine artifacts.

So the newer ruling and the shipped one COLLIDE, and this module does not get to resolve
that quietly in a volume lane. What it does instead is everything that can be enforced
today without reverting a shipped ruling, and it names the residue rather than hiding it.

WHAT IS ENFORCED (A1-A4)
  A1  NO equippable artifact is reachable from any mod loot surface, except the
      committed `R185_CRAFT_REAGENT_PIN` roster.
  A2  every PIN is still EARNED, re-derived from the bytes: a pinned record must still
      be named as a reagent by a real uber formula. A pin whose justification has
      evaporated is dead config and reds - the D5-pin / MI_NO_LIVE_CARRIER discipline.
  A3  every PIN is still LIVE. A pin for a record nothing reaches any more is also dead
      config, and it reds from the other side, so the roster can only shrink honestly.
  A4  the scroll discriminator is re-proved every run (see below), because a rule that
      silently stops discriminating would either exempt all 299 artifacts or none.

A SCROLL IS NOT AN ARTIFACT, AND THE DIFFERENCE IS MEASURED, NOT ASSUMED
-------------------------------------------------------------------------
All 299 `ItemArtifact` records in the mod database sit on `ItemArtifact.tpl`, so the
engine `Class` cannot tell a Divine artifact from a mercenary-hire scroll. What DOES
separate them is the skill each grants: MEASURED on b83, 158 of the 299 point
`itemSkillName` at `records\skills\scroll skills\...` and 141 do not. The 158 are the
merc and spell scrolls that every chest in the base game has always paid; the 141 are
the equippable artifacts (Divine 42, Greater 33, Lesser 66) a player wears. Reading
Will's "artifacts" as the 141 is the only reading that is both implementable and true
to what a player calls an artifact: a literal all-299 rule would demand stripping merc
scrolls out of the base game's own `04_*_misc` tables, changing every chest in the
campaign, which is neither what he asked for nor something a loot lane may do.

WHAT IS NOT ENFORCED, AND WHAT IT WOULD COST (`BL-R240-DEBT-2`)
----------------------------------------------------------------
FULL compliance - zero equippable artifacts, roster included - is a small, bounded
change and it belongs to the craft lane, not here:
  * delete the `svc_craft_reagents_artifact_l01` member from `04_l_misc` (one row);
  * `svc_craft_thrown`'s rules G1 and G4 then RED on those six, so they need a new
    exemption class, the same shape as the existing MI/green one: "a reagent that is
    itself a craftable". `docs/CHEST_DROP_MATRIX.md` 6.5 already reaches that verdict
    on its own - both affected craftables are marked "No fix needed ... this recipe is
    a craft-a-craft by base-game design" - so 42-of-42 completability survives.
It is one lane, and it is not this one (one lane per problem; this lane's own scope
proof forbids it from touching a member). Until it runs, A1's roster IS the ruling's
enforcement surface: nothing NEW can leak, and the day the craft lane removes the row,
A3 reds the now-dead pin and the roster deletes itself.

Shared by `tools/gate_chest_artifacts.py` (standalone), the in-build gate
`tools/patches/loot_volume_trim.verify()` and `tools/debug/negtest_loot_volume.py`.
"""
import sys
from pathlib import Path

if __name__ == '__main__' or __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

import svc_armor_breadth as SAB
import svc_craft_thrown as SCT
import svc_loot_breadth as SLB
import svc_loot_distribution as SLD

# The folder every scroll's granted skill lives in. MEASURED (158 of 299 records on
# the b83 arz); A4 re-proves it every run, so a base-game reorganisation that moved
# these records cannot silently turn the whole roster into "equippable".
SCROLL_SKILL_MARK = '\\skills\\scroll skills\\'
# Below this the discriminator has stopped discriminating and A4 says so rather than
# letting the gate report a clean sweep it did not perform. The real count is 158.
MIN_SCROLL_RECORDS = 50

# ── THE PIN: R-185's six divine-artifact craft reagents ──────────────────────
# Committed by NAME so the roster cannot grow by accident, and re-derived by RULE
# (A2/A3) so it cannot outlive its reason. Every entry carries the ruling that put it
# there; an entry with no live justification fails the build.
R185_CRAFT_REAGENT_PIN = {
    r'records\xpack\item\artifacts\e_da_crescentmoonofartemis.dbr':
        'R-185 divine-artifact craft reagent (Mortok\'s Skull chain)',
    r'records\xpack\item\artifacts\e_da_demetersbounty.dbr':
        'R-185 divine-artifact craft reagent (The All-Seeing Eye chain)',
    r'records\xpack\item\artifacts\l_da_goldeneyeofsunwukong.dbr':
        'R-185 divine-artifact craft reagent (The All-Seeing Eye chain)',
    r'records\xpack\item\artifacts\l_da_ikonofzeus.dbr':
        'R-185 divine-artifact craft reagent (Mortok\'s Skull chain)',
    r'records\xpack\item\artifacts\l_da_mardukstabletofdestiny.dbr':
        'R-185 divine-artifact craft reagent (The All-Seeing Eye chain)',
    r'records\xpack\item\artifacts\l_da_thothsglory.dbr':
        'R-185 divine-artifact craft reagent (Mortok\'s Skull chain)',
}


def is_scroll(d, path):
    return SCROLL_SKILL_MARK in SLD._n(d.gv(path, 'itemSkillName') or '')


def is_equippable_artifact(d, path):
    """Will's "artifacts": an ItemArtifact a player WEARS, not a scroll they read."""
    return d.cls(path) == 'ItemArtifact' and not is_scroll(d, path)


def reachable_artifacts(db, lk=None):
    """{artifact record: sorted[surface labels]} over every mod loot surface."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    dist = SLD.Distributor(d)
    hits = {}
    for label, tables, _w, _tier in SAB.all_surfaces(db, lk):
        for t in tables:
            # `per_item_all` is the UNFILTERED expectation, so an artifact is caught
            # whatever its classification - filtering by `Legendary` first is how an
            # Epic-tier leak would have walked straight past this check.
            for it in SLD.ChestProfile(d, dist, t, 1, 'Legendary').per_item_all:
                if is_equippable_artifact(d, it):
                    hits.setdefault(SLD._n(it), set()).add(label)
    return {k: sorted(v) for k, v in hits.items()}


def problems(db, lk=None):
    """A1-A4. Returns a list of problem strings, empty when clean."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    out = []

    # A4 - the discriminator must still discriminate.
    n_scroll = sum(1 for p in db.record_names()
                   if d.cls(p) == 'ItemArtifact' and is_scroll(d, p))
    if n_scroll < MIN_SCROLL_RECORDS:
        out.append(
            "A4 only %d ItemArtifact record(s) resolve a `%s` skill (expected >= %d). "
            "The scroll discriminator has stopped discriminating, so this gate is "
            "either exempting every artifact in the game or none of them, and its PASS "
            "line would claim a sweep it did not perform."
            % (n_scroll, SCROLL_SKILL_MARK.strip('\\'), MIN_SCROLL_RECORDS))
        return out

    reach = reachable_artifacts(db, lk)
    pinned = {SLD._n(k): v for k, v in R185_CRAFT_REAGENT_PIN.items()}

    # A1 - nothing off the roster may be reachable.
    for rec in sorted(reach):
        if rec in pinned:
            continue
        out.append(
            "A1 the equippable artifact %s is reachable from %d mod loot surface(s) "
            "(%s) and is NOT on the R-185 craft-reagent roster. Will 2026-08-11: "
            "\"artifacts should never drop from chests\"."
            % (rec, len(reach[rec]), ', '.join(reach[rec][:3])))

    # A2/A3 - every pin is still earned AND still live.
    users = SCT.reagent_universe(db, lk)
    for rec, why in sorted(pinned.items()):
        if rec not in reach:
            out.append(
                "A3 the roster pins %s (%s) but nothing reaches it any more. A pin with "
                "no live leak is DEAD CONFIG: delete it, and if the roster empties, "
                "delete the exemption with it - Will's ruling would then hold outright."
                % (rec, why))
            continue
        if rec not in users:
            out.append(
                "A2 the roster pins %s (%s) but NO uber formula names it as a reagent "
                "any more, so the R-185 justification that earned the exemption is "
                "gone while the artifact keeps dropping. Re-derive the pin or remove "
                "the loot row." % (rec, why))
    return out


def pass_line(db, lk=None):
    """One sentence for the build log, stating exactly what was and was not enforced."""
    lk = lk or SLB.Lookup(db)
    d = SLD.Db(db)
    reach = reachable_artifacts(db, lk)
    n_equip = sum(1 for p in db.record_names() if is_equippable_artifact(d, p))
    return ("%d of %d equippable artifact(s) unreachable from every mod chest, hoard "
            "and orb; the remaining %d are the pinned R-185 craft reagents, each "
            "re-proved still live and still named by a formula. Scrolls are out of "
            "scope by measurement (%d of them), not by assumption. "
            "*** THIS PASS IS NOT COMPLIANCE: Will's ruling was \"artifacts should never "
            "drop from chests\" and what is asserted here is \"never EXCEPT %d pinned by "
            "name\". The exemption exists because R-185 - Will's own ruling - put them "
            "there, so a literal zero-artifact gate would red the shipped build. "
            "RATIFICATION OR THE ONE-LANE FOLLOW-UP IS A WILL DECISION: BL-R240-DEBT-2 ***"
            % (n_equip - len(reach), n_equip, len(reach),
               sum(1 for p in db.record_names()
                   if d.cls(p) == 'ItemArtifact' and is_scroll(d, p)),
               len(reach)))
