"""mastery_ui_audit - cross-mastery skill-tree UI fix (build38, Will 2026-07-13).

Will's report (verbatim intent): in EARTH mastery two skills have NO icons and are
OUT OF PLACE at the start of the Rupture chain; RUPTURE APPEARS TWICE; the Rupture
chain should start lower; "issues like this across ALL masteries"; MANY mastery
screens have a BLACK BACKGROUND.

ROOT CAUSE (proven against the LIVE build36 arz + the b37 code state; full evidence
in docs/reports/b38_mastery_ui_audit.md):

  1. BROKEN ICONS - the build36 LANE-B SVAERA graft (build_svc_database.py
     graft_svaera_mastery_skills) imported 14 player skills whose icon bitmaps point
     into `_DRX_Textures\\...` - an arc SVAERA ships but this mod does NOT (we ship
     DRXtextures.arc, a different arc; the basenames resolve in NO shipped arc). Seven
     grafted skills across FIVE masteries render iconless. The other graft members
     already point at base-game DLC arcs (XPack3\\UI\\...) which resolve fine, so the
     graft author simply used the wrong prefix on the SVAERA-custom icons. FIX: repoint
     each broken icon to the resolvable equivalent (the exact icon exists in base
     XPack3\\UI for firenova / activeblock / dreamimage; a thematically-matched base
     InGameUI/XPack3 icon for the rest). All targets .tex-resolved against the shipped
     mod arcs UNION the base-game arcs.

  2. DUPLICATE "Rupture"/"Flare" (Earth) - SV 0.98i (amgoz1, the untouchable design
     bible) deliberately renamed the base game's Earth "Flame Surge" line to display
     "Rupture" (drxflamesurge) + "Flare" (drxflamesurge_flamearch); PROVEN identical in
     098i AND sv0.9 (base AE still shows tagSkillName113 "Flame Surge" / 103 "Flame
     Arch"). The build36 graft then ADDED a second, bow-variant "Rupture" line
     (drxrupture + drxrupture_burning + drxrupture_flare) that reuses tagRuptureNAME /
     tagFlareNAME -> two "Rupture" and two "Flare" on screen. The correctly-wired, live,
     bible-canonical Rupture is drxflamesurge (staff; RangedOneHand=1; matches its
     tooltip); it is SV-original and UNTOUCHED. We de-duplicate on the GRAFT side only
     (build36 records, editable): drxrupture -> "Flame Surge" (tagSkillName113) and
     drxrupture_flare -> "Flame Arch" (tagSkillName103). Those two base-game name/desc
     tags were FREED by SV's own rename and are UNUSED in the mod, so the graft line
     reads "Flame Surge / Burning Bolts / Flame Arch / Fire Nova" with zero collisions.
     Base-game tags resolve at runtime and are NOT mod-owned, so validate_tags does not
     require them in Text.arc (identical to how the graft already uses
     x3tagSkillEarthFireNova + tagSkillName185).

  3. INTERLEAVED / INVERTED Earth Rupture chain - the graft crammed firenova / rupture
     / burning / flare into the free cells of Earth UI column x=428, INTERLEAVING them
     with the existing Ring-of-Flame chain (ringofflame, softenmetal) + Spontaneous
     Combustion, and with the base skill (drxrupture) sitting HIGH (y=93) above its own
     modifiers. FIX: reflow column 428 so each chain is contiguous and each base sits
     at the bottom (higher y) with modifiers stacking up - Ring-of-Flame (403,341),
     then the graft chain rupture(279)->burning(217)->flare(155) "starting lower", then
     the two standalones on top (spontaneous 93, firenova 31). Only UI-button records
     (skillNN.dbr) move; no skill VALUE changes. Earth (mastery 3) is NOT golden-tracked
     (the A7 golden covers only masteries 5/6), so no waiver is required; this is the
     ho-ui F5 UI-defect-fix precedent applied to Earth.

  4. BLACK BACKGROUND - EVERY mastery's skillpanebasebitmap/reallocation points at
     `SkillsPanel\\skillbackgrounddiablo.tex`, an arc that resolves in NO shipped or
     base arc (proven). The b37-merged hunting_occult_ui already repoints masteries 1-8
     to their base-game `InGameUI\\Skills\\<Class>SkillBackground01.tex` (all present).
     The remaining black screen is the DREAM mastery (xpack mastery 9), which
     hunting_occult_ui does not cover. No dedicated Dream backdrop ships (base AE has no
     Dream bg override + no DreamSkillBackground texture exists), so we repoint Dream to
     the resolving Spirit backdrop (Dream is the psionic/spirit-adjacent mastery) - a
     best-effort fix that is strictly better than the black pane.

  5. Nature "Sylvan Protection" (drx_nymph_petmodifier_rootwave, a graft pet-modifier,
     absent from 098i) shipped with NO skillUpBitmapName at all -> iconless button. FIX:
     give it the resolving base Sylvan Nymph icon (the pet it modifies). Its
     skillDisplayName is also empty (a residual graft defect documented in the report;
     the display-tag repair is left for a targeted follow-up since it needs the exact
     x3 Sylvan Protection tag and touches design identity).

NOT changed (documented in the report, deliberately out of scope for a safe UI pass):
  - Storm UI slot25 -> drxspellbreaker_spellshock2.dbr is a PRE-EXISTING SV-ORIGINAL
    dead reference (present verbatim in 098i; the referenced skill has never existed in
    any source). Repointing would either duplicate slot14 (which already holds the real
    _spellshock) or invent a skill; it needs Will's design call, so it is reported, not
    touched.
  - The SV-original drxflamesurge "Rupture"/"Flare" line and its swapped-icon quirk are
    amgoz1 design and stay untouched.

CONTRACT: patches-registry module - MODULE_NAME + apply(db, tags). Disjoint from every
other b37/b38 module (hunting_occult_ui owns mastery 1-8 backgrounds + O/H button
shapes; this owns the DREAM background, the seven graft icons, the Earth graft rename +
reflow, and the Nature graft icon). Runs after the monolith graft so all target records
exist. Fail-loud on any unexpectedly-absent target (an upstream structural change).
"""

MODULE_NAME = "Cross-mastery skill-tree UI fix (graft icons, Earth Rupture de-dup + reflow, Dream bg)"

# ---------------------------------------------------------------------------
# Path helpers
_SK = "records\\skills\\%s"                                   # + mastery\\name.dbr
_UI = "records\\ingameui\\player skills\\mastery %d\\%s"      # + slot file
_DREAM_UI = "records\\xpack\\ui\\skills\\mastery 9\\%s"

# ---------------------------------------------------------------------------
# 1 + 5: broken graft icons -> resolving equivalents.  (skill record, up.tex, down.tex)
# Every target verified present in the shipped mod arcs UNION the base-game arcs.
_ICON_FIXES = [
    # Warfare - Fissure (Slam modifier); no base "fissure" icon, use the Onslaught AoE.
    (_SK % r"warfare\drx_clubslam_fissure.dbr",
     r"InGameUI\Icons\Skills\Warfare\OnslaughtUp01.tex",
     r"InGameUI\Icons\Skills\Warfare\OnslaughtDown01.tex"),
    # Defense - Perfect Block == Ragnarok Active Block (EXACT icon, base XPack3\UI).
    (_SK % r"defensive\drx_activeblock.dbr",
     r"XPack3\UI\icons\skills\activeblock_up.tex",
     r"XPack3\UI\icons\skills\activeblock_down.tex"),
    # Earth - Fire Nova == Ragnarok Fire Nova (EXACT icon, base XPack3\UI).
    (_SK % r"earth\drx_firenova.dbr",
     r"XPack3\UI\icons\skills\firenova_up.tex",
     r"XPack3\UI\icons\skills\firenova_down.tex"),
    # Earth - Burning Bolts (staff fire projectiles) -> Barrage icon.
    (_SK % r"earth\drxrupture_burning.dbr",
     r"InGameUI\Icons\Skills\Earth\BarrageUp01.tex",
     r"InGameUI\Icons\Skills\Earth\BarrageDown01.tex"),
    # Earth - drxrupture_flare renamed to "Flame Arch" below -> the Flame Arch icon.
    (_SK % r"earth\drxrupture_flare.dbr",
     r"InGameUI\Icons\Skills\Earth\FlameArchUp01.tex",
     r"InGameUI\Icons\Skills\Earth\FlameArchDown01.tex"),
    # Storm - Frost Nova (expanding frost ring) -> Freeze icon.
    (_SK % r"storm\drxfrostnova.dbr",
     r"InGameUI\Icons\Skills\Storm\FreezeUp01.tex",
     r"InGameUI\Icons\Skills\Storm\FreezeDown01.tex"),
    # Dream - Dream Image == Ragnarok Dream Image (EXACT icon, base XPack3\UI).
    # NB: Dream skills live under records\xpack\skills\dream\ (not records\skills\).
    (r"records\xpack\skills\dream\drx_summoncopy.dbr",
     r"XPack3\UI\icons\skills\dreamimage_up.tex",
     r"XPack3\UI\icons\skills\dreamimage_down.tex"),
    # Nature - Sylvan Protection (nymph pet-modifier) had NO icon at all -> nymph icon.
    (_SK % r"nature\drx_nymph_petmodifier_rootwave.dbr",
     r"InGameUI\Icons\Skills\Nature\SilvanNymphUp01.tex",
     r"InGameUI\Icons\Skills\Nature\SilvanNymphDown01.tex"),
]

# 2: Earth duplicate-name de-dup - relabel the GRAFT records to the free base tags SV
# vacated (drxflamesurge/flamearch, the SV-canonical Rupture/Flare, stay untouched).
# (skill record, new name tag, new desc tag, new up.tex, new down.tex or None)
_RENAME_FIXES = [
    (_SK % r"earth\drxrupture.dbr",
     "tagSkillName113", "tagSkillDescription113",            # "Flame Surge"
     r"InGameUI\Icons\Skills\Earth\FlameSurgeUp01.tex",
     r"InGameUI\Icons\Skills\Earth\FlameSurgeDown01.tex"),
    (_SK % r"earth\drxrupture_flare.dbr",
     "tagSkillName103", "tagSkillDescription103",            # "Flame Arch"
     None, None),                                            # icon set by _ICON_FIXES
]

# 3: Earth column-428 reflow (de-interleave; graft chain contiguous, base lower).
# (ui slot file, expected skillName basename, new x, new y).  We assert the slot still
# holds the expected skill before moving it (fail-loud if the layout drifted upstream).
_EARTH_REFLOW = [
    ("skill10.dbr", "drxringofflame_softenmetal", 428, 341),   # was 279
    ("skill26.dbr", "drxrupture",                 428, 279),   # was 93  (graft base, lower)
    ("skill28.dbr", "drxrupture_flare",           428, 155),   # was 341
    ("skill23.dbr", "drxspontaneouscombustion",   428,  93),   # was 155
]

# 4: Dream (xpack mastery 9) background repoint (1-8 handled by hunting_occult_ui).
_DREAM_BG = [
    ("skillpanebasebitmap.dbr",         r"InGameUI\Skills\SpiritSkillBackground01.tex"),
    ("skillpanereallocationbitmap.dbr", r"InGameUI\Skills\SpiritSkillReallocationBackground01.tex"),
]


def _first(v):
    return v[0] if isinstance(v, list) else v


def apply(db, tags):
    """Repoint 7 broken graft icons + the Nature graft icon, de-duplicate the Earth
    graft Rupture/Flare labels, reflow Earth column 428, and repoint the Dream
    background. Fail-loud if any target record/field is unexpectedly absent. `tags` is
    unused - every referenced text tag (tagSkillName113/103 + descriptions) is a
    base-game tag that resolves at runtime (validate_tags does not require base tags)."""
    print("\n=== mastery_ui_audit: cross-mastery skill-tree UI fix (build38) ===")

    def _resolve(rec):
        """Case-insensitive record lookup; fail-loud if absent."""
        if db.has_record(rec):
            return rec
        low = rec.lower().replace('/', '\\')
        for n in db.record_names():
            if n.lower().replace('/', '\\') == low:
                return n
        raise SystemExit("mastery_ui_audit: expected record missing: %s "
                         "(upstream structure changed?)" % rec)

    def _require_field(rec, field):
        if db.get_field_value(rec, field) is None:
            raise SystemExit("mastery_ui_audit: %s lacks expected field %s" % (rec, field))

    # 1 + 5: icon repoints (graft skill records - build36 additions, editable).
    for skill, up, down in _ICON_FIXES:
        rec = _resolve(skill)
        db.set_field(rec, "skillUpBitmapName", up)
        db.set_field(rec, "skillDownBitmapName", down)
        print("  icon  %-52s -> %s" % (skill.rsplit('\\', 1)[-1], up.rsplit('\\', 1)[-1]))
    print("  graft icons repointed: %d (7 _DRX_Textures + 1 empty) -> resolving arcs" % len(_ICON_FIXES))

    # 2: Earth Rupture/Flare de-dup (relabel the GRAFT records only).
    for skill, name_tag, desc_tag, up, down in _RENAME_FIXES:
        rec = _resolve(skill)
        _require_field(rec, "skillDisplayName")
        _require_field(rec, "skillBaseDescription")
        db.set_field(rec, "skillDisplayName", name_tag)
        db.set_field(rec, "skillBaseDescription", desc_tag)
        if up:
            db.set_field(rec, "skillUpBitmapName", up)
            db.set_field(rec, "skillDownBitmapName", down)
        print("  rename %-24s -> %s (%s)" % (skill.rsplit('\\', 1)[-1], name_tag,
                                             (up or 'icon via _ICON_FIXES').rsplit('\\', 1)[-1]))
    print("  Earth graft de-dup: drxrupture -> Flame Surge, drxrupture_flare -> Flame Arch "
          "(SV drxflamesurge stays the canonical Rupture)")

    # 3: Earth column-428 reflow (UI-button positions only).
    for slot_file, expect, x, y in _EARTH_REFLOW:
        rec = _resolve(_UI % (3, slot_file))
        sn = _first(db.get_field_value(rec, "skillName")) or ""
        base = sn.rsplit('\\', 1)[-1].lower()
        if base.endswith('.dbr'):
            base = base[:-4]
        if base != expect.lower():
            raise SystemExit(
                "mastery_ui_audit: Earth %s holds %r, expected %s - layout drifted; "
                "reconcile the reflow before shipping" % (slot_file, sn, expect))
        db.set_field(rec, "bitmapPositionX", x, 0)   # dtype 0 = INT (match existing)
        db.set_field(rec, "bitmapPositionY", y, 0)
        print("  reflow Earth %-12s (%s) -> (%d,%d)" % (slot_file, expect, x, y))
    print("  Earth col-428 reflow: Ring-of-Flame + graft Rupture chain now contiguous, "
          "base lower; standalones on top")

    # 4: Dream (xpack mastery 9) background repoint.
    for bg_file, tex in _DREAM_BG:
        rec = _resolve(_DREAM_UI % bg_file)
        _require_field(rec, "bitmapName")
        db.set_field(rec, "bitmapName", tex)
        print("  Dream bg %-34s -> %s" % (bg_file, tex.rsplit('\\', 1)[-1]))

    print("=== mastery_ui_audit done: %d icons, %d renames, %d reflow, %d Dream bg ==="
          % (len(_ICON_FIXES), len(_RENAME_FIXES), len(_EARTH_REFLOW), len(_DREAM_BG)))
