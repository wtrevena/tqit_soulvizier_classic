r"""soul_identity - b97: A CREATURE MUST NOT DROP ANOTHER NAMED CREATURE'S SOUL.

WILL'S REPORT (verbatim, 2026-07-27):
    "we also need to do an audit of the hero monsters vs the souls that they drop
     since i can see that some of the heroes are dropping the wrong souls or souls
     for other boss monsters i think"

Full audit + the classified table: docs/reports/b97_soul_identity_audit.md.

--------------------------------------------------------------------------------
THE DEFECT (root cause, two layers)
--------------------------------------------------------------------------------
A TQ monster's IDENTITY is its `description` tag (the name the player reads), NOT
its .dbr filename. The base game reuses ONE hero .dbr filename across SEVERAL
DIFFERENT named heroes, distinguished only by the numeric suffix and their own
description tag:

    records\creature\monster\ratman\hero_wheedletongue_39.dbr -> "Wheedletongue the Magnificent"
    records\creature\monster\ratman\hero_wheedletongue_41.dbr -> "Fesil the Quick"
    records\creature\monster\ratman\hero_wheedletongue_43.dbr -> "Sinnet Patchfur"

`build_svc_database.wire_souls_to_monsters` matches souls to monsters by FILENAME
(`_monster_clean_name` -> 'hero_wheedletongue'), so all three of those records
qualify for the Wheedletongue soul. amgoz1's SV 0.98i data made the same
filename-shaped assumption and pre-attached the donor's soul to the whole family.
Our build then does the second half of the damage: the "already had souls" branch
of `wire_souls_to_monsters` ACTIVATES every Hero/Boss/Quest that carries soul loot
(chanceToEquipFinger2 -> 50/66/25), including the pairings SV shipped DEAD at
chance 0.0. Latent upstream mis-pairings therefore became live player-visible
drops - which is exactly what Will is seeing.

The pre-existing F1 gate (`build_svc_database._verify_no_fuzzy_cross_wire`) cannot
catch this: it scores the soul name against the monster's FILENAME, the very axis
that is wrong ('wheedletongue' IS a substring of 'hero_wheedletongue'), and it
additionally whitelists every pairing SV 0.98i authored. This module closes the
IDENTITY dimension the rank-dimension yeti fix (419 records) never covered.

--------------------------------------------------------------------------------
THE RULE (data-derived; no hand-list decides who loses a drop)
--------------------------------------------------------------------------------
For every soul NAME S (the text the player reads on the item), let CARRIERS(S) =
the records with a LIVE soul drop (chanceToEquipFinger2 > 0) whose
lootFinger2Item1 references an item displaying S.

    If SOME carrier's display name identity-matches S,
    then every OTHER carrier whose display name does NOT match is an
    IDENTITY THIEF -> chanceToEquipFinger2 = 0.

    If NO carrier identity-matches S, NOTHING is touched.

ROUND 2 (2026-07-28) closed two holes the first pass shipped with; both are
proven by planted tests (tools/contracts/tests_soul_identity_negative.py):

  * SCOPE. The roster was gated on the path containing \creature(s)\, which
    silently skipped 97 LIVE carriers - all of records\drxcreatures\ (25 records
    of shipping DRX/Urder content), records\test\, records\item\equipmentring\
    soul\test\ and the pet trees. One of the skipped records was a REAL
    mismatch of exactly the class Will reported: 'Akara' (a D2 NPC) dropping
    "Kallixenia ~ Liche Queen Soul" at 66%, wired by our OWN
    apply_svc_patches._create_kallixenia_soul. The roster is now the whole
    database minus pets/proxies (see _is_soul_carrier).
  * GROUPING. Carriers were grouped by the soul .dbr FILENAME family, which is
    the same filename-is-identity mistake the module exists to punish. Two
    DIFFERENT soul items can share a basename (soul\abyssalliche\kallixenia_*
    and soul\svc_uber\kallixenia_*) and two different items can share a NAME.
    Carriers are now grouped by the soul's DISPLAY NAME, which is the only
    thing the player can see and therefore the only thing "wrong soul" can mean.

The second clause is load-bearing and is why this module cannot orphan content.
It structurally preserves the two legitimate share patterns, with no whitelist:

  * ARCHETYPE souls - a soul named for a COMMON monster type (Satyr Fire Magi,
    Sandwraith, Diseased Vulture, Maenad Sorceress, Awakened Dead Soldier) whose
    only live carriers are that family's named uniques. The archetype's own
    Common/Champion records carry the loot ref but are gated dead by the yeti
    rank-fix, so no carrier "owns" the name and the named hero remains the only
    way to obtain it. Zeroing those would make the soul UNOBTAINABLE.
  * NAME-DRIFT 1:1 - SV renamed the monster but not its soul ("Wither Mound" <->
    Speckled Jim Soul, "Shriekbrood the Collector" <-> Grimshell Soul, "Skull
    Spine" <-> Spinebone Soul, "Vile Crawl" <-> Vilerotter Soul, "Clazomenaeus
    the Unstoppable" <-> Crowboar Soul, "The Ethereal One" <-> "The Etheral One
    Soul" [sic]). Sole carrier, nobody's identity is stolen: you kill that
    creature, you get that creature's soul, spelled differently. Renaming those
    is a TEXT/design decision (amgoz1 creative bar) -> listed for Will, untouched.

Mod-authored themed souls ("Soul of the Gaoler" for Alkyoneus the Hoard Unbound,
"Ash of the Funeral Games" for the Helepolis, "Marshal's Command" for Menoetes)
are likewise sole-carrier and therefore untouched by construction.

IDENTITY MATCHING is done on DISPLAY TEXT only - never on the .dbr filename, the
axis that caused the defect. A monster name may carry a "~ Family" epithet
("Gorgon Queen ~ Stheno"); each segment is tried. A soul name may be
"<Name> Soul" or "Soul of the <Name>"; both shapes are reduced to the core name.

--------------------------------------------------------------------------------
SCOPE / SAFETY
--------------------------------------------------------------------------------
* Writes exactly ONE field, `chanceToEquipFinger2`, and only ever DOWNWARD to 0.0.
  No soul ITEM record, no loot ref, no tag, no pet, no skill, no pool, no map is
  touched. lootFinger2Item1 is deliberately LEFT INTACT (the same shape as the A4
  Aphiastas-zero and the R-45 tombguardian deny-list: detach the roll, keep the
  data, so the change is reviewable and reversible).
* RETIREMENT PROTOCOL: nothing is deleted. Every zeroed soul remains obtainable
  from its rightful owner - proven per-family in apply() (a family is only ever
  zeroed when a matching carrier EXISTS and stays live).
* REVIEW GATE: the derived verdict is asserted against _REVIEWED (below), the set
  a human classified in the b97 audit. _REVIEWED is NOT the mechanism that decides
  who loses a drop - the RULE decides - it is the proof that the current data's
  verdict is the one that was reviewed. If content drift changes the verdict the
  build FAILS LOUD asking for review rather than silently zeroing a boss's soul.

ORDERING: registered after every soul-wiring/drop-rate module (incl.
toxeus_souls_100) so apply() sees the FINAL carrier set. verify() re-runs the rule
over the FINAL merged db in step 4 (after the whole gate battery + the testing
forcer) and fails the build if any identity thief survives - the permanent,
list-free regression gate.
"""
import re

from arz_patcher import DATA_TYPE_FLOAT

MODULE_NAME = "soul identity: no creature drops another named creature's soul (b97)"

_CHANCE = 'chanceToEquipFinger2'
_LOOT = 'lootFinger2Item1'

# Words that carry no identity signal when comparing a monster name to a soul name.
_STOP = {'the', 'of', 'a', 'an', 'and', 'soul', 'souls'}

# Minimum length for a concatenated-name containment hit (guards 'ben' in
# 'bonescourge'-style accidental substring matches).
_MIN_CONCAT = 4
# Minimum length for a single shared word to count as an identity signal.
_MIN_WORD = 4


# ── the REVIEWED verdict (proof of human review, NOT the decision mechanism) ──
# monster record (lower, backslashes) -> (monster display, the SOUL NAME it
# wrongly drops, the rightful owner that keeps it live). Classified in the b97
# audit from the deployed arz + SV 0.98i + TQAE base provenance; see
# docs/reports/b97_soul_identity_audit.md for the full table and per-row cause.
_REVIEWED = {
    # -- base-game hero-filename reuse (one .dbr family, several named heroes) --
    r"records\creature\monster\ratman\hero_wheedletongue_41.dbr":
        ("Fesil the Quick", 'Wheedletongue the Magnificent Soul',
         "Wheedletongue the Magnificent"),
    r"records\creature\monster\ratman\hero_wheedletongue_43.dbr":
        ("Sinnet Patchfur", 'Wheedletongue the Magnificent Soul',
         "Wheedletongue the Magnificent"),
    r"records\creature\monster\scorpos\hero_kaaltspeartail_30.dbr":
        ("Errak Bonecarver", 'Kaalt Speartail Soul', "Kaalt Speartail"),
    r"records\creature\monster\scorpos\hero_kaaltspeartail_33.dbr":
        ("Sartt Soulrender", 'Kaalt Speartail Soul', "Kaalt Speartail"),
    r"records\creature\monster\neanderthal\hero_grom_31.dbr":
        ("Korat Bearkin", 'Grom Soul', "Grom"),
    r"records\creature\monster\djinn\hero_adarathelovely_43.dbr":
        ("Raghd Bloatworm", 'Adara the Lovely Soul', "Adara the Lovely"),
    r"records\creature\monster\tropicalarachnos\hero_princech'kik't_37.dbr":
        ("Prince Ch'kik't the Horrible", "Z'kar Flamespinner Soul",
         "Z'kar Flamespinner"),
    # -- SV/mod clone kept the donor's soul, description changed --
    r"records\creature\monster\ratman\um_inkeyes_45.dbr":
        ("Blood-Eyes", 'Wheedletongue the Magnificent Soul',
         "Wheedletongue the Magnificent"),
    r"records\creature\monster\ratman\um_inkeyes2_45.dbr":
        ("Blood-Eyes", 'Wheedletongue the Magnificent Soul',
         "Wheedletongue the Magnificent"),
    r"records\creature\monster\shadowstalker\um_wahr_33.dbr":
        ("Wahr'Ner Shadowpaw", "Nephi'tek the Lasher Soul", "Nephi'tek the Lasher"),
    r"records\creature\monster\shadowstalker\us_nazur_34.dbr":
        ("Nazur the Shrouded", "Nephi'tek the Lasher Soul", "Nephi'tek the Lasher"),
    r"records\creature\monster\naiad\ur_masai_43.dbr":
        ("Masai-yin the Grovekeeper", 'Syrinx of the Tainted Meadow Soul',
         "Syrinx of the Tainted Meadow"),
    r"records\creature\monster\naiad\ur_uber_45.dbr":
        ("Xuannu the Twilight Matron", 'Syrinx of the Tainted Meadow Soul',
         "Syrinx of the Tainted Meadow"),
    r"records\creature\monster\limos\um_morbi_17.dbr":
        ("Morbi", 'Venemurax Soul', "Venemurax"),
    r"records\creature\monster\carrionbird\us_mormo_16.dbr":
        ("Mormo", 'Storm Crow Soul', "Storm Crow"),
    r"records\creature\monster\antlion\us_frostscarab_35.dbr":
        ("Daechalcos", 'Scarabaeus Soul', "Scarabaeus the Desert King"),
    r"records\creature\monster\gorgon\us_poisonsiren_14.dbr":
        ("Thelxiepeia Venomlip", 'Aquardia the Coral Queen Soul',
         "Aquardia, the Coral Queen"),
    # -- our own fuzzy filename wire (no SV/base precedent for the pairing) --
    r"records\creature\monster\scorpion\um_rocksting_29.dbr":
        ("Colossal Scorpion", 'Rocksting Soul', "Rock Sting"),
    # ── ROUND 2: the 4 carriers the \creature(s)\ scope predicate hid ─────────
    # OUR OWN wire. apply_svc_patches._create_kallixenia_soul points a bespoke
    # "Kallixenia ~ Liche Queen Soul" at the DRX D2-NPC record 01_akara, whose
    # description tag (tagD2NPCakara) reads "Akara". The real Kallixenia
    # (xpack\...\abyssalliche\xsq02_lichequeen_36) drops an identically-NAMED
    # soul at the same 66%, so the player sees Akara handing out the Liche
    # Queen's soul - precisely Will's report. See docs report sec 8 for the
    # Will decision (zero the roll now vs. rename the record to Kallixenia).
    r"records\drxcreatures\xurder\d2npc\01_akara.dbr":
        ("Akara", 'Kallixenia ~ Liche Queen Soul', "Kallixenia ~ Liche Queen"),
    # SV's own legacy soul\test\ monsters: the us_lysiaspellbreaker_15 trio
    # carries Lysia Spellbreaker's soul but a copy-pasted "Nenea Sharpclaw"
    # description. Lysia Spellbreaker's real record keeps the soul live.
    r"records\item\equipmentring\soul\test\us_lysiaspellbreaker_15.dbr":
        ("Nenea Sharpclaw", 'Lysia Spellbreaker Soul', "Lysia Spellbreaker"),
    r"records\item\equipmentring\soul\test\us_lysiaspellbreaker_15_e.dbr":
        ("Nenea Sharpclaw", 'Lysia Spellbreaker Soul', "Lysia Spellbreaker"),
    r"records\item\equipmentring\soul\test\us_lysiaspellbreaker_15_l.dbr":
        ("Nenea Sharpclaw", 'Lysia Spellbreaker Soul', "Lysia Spellbreaker"),
}


# ── REVIEWED item-level detachments (see _item_detach_guard) ─────────────────
# Zeroing a thief can leave a specific soul ITEM record with no live carrier
# even though its NAME stays obtainable from the rightful owner (two distinct
# item families can share one display name). That is real content going dark,
# so it must be reviewed per item, never silent.
_ACCEPTED_ITEM_DETACH = {
    r"records\item\equipmentring\soul\svc_uber\kallixenia_soul_n.dbr":
        "b97r2: our own bespoke Kallixenia soul, wired ONLY to 01_akara "
        "('Akara'). The NAME 'Kallixenia ~ Liche Queen Soul' stays obtainable "
        "from the real Kallixenia (soul\\abyssalliche\\kallixenia_soul_*). The "
        "item record is kept intact (retirement protocol - nothing deleted); "
        "re-attaching it is a one-line Will decision (report sec 8).",
    r"records\item\equipmentring\soul\svc_uber\kallixenia_soul_e.dbr": "as _n",
    r"records\item\equipmentring\soul\svc_uber\kallixenia_soul_l.dbr": "as _n",
}


# ============================================================================
# text helpers
# ============================================================================
def _strip_color(s):
    """'{^F}Stone Hide Soul' -> 'Stone Hide Soul'."""
    return re.sub(r'\{\^.\}', '', str(s or ''))


def _concat(s):
    return re.sub(r'[^a-z0-9]+', '', _strip_color(s).lower())


def _words(s):
    toks = re.sub(r'[^a-z0-9]+', ' ', _strip_color(s).lower()).split()
    return {t for t in toks if t not in _STOP and len(t) >= _MIN_WORD}


def _soul_core(text):
    """'{^F}Stone Hide Soul' -> 'Stone Hide'; '{^F}Soul of the Gaoler' -> 'Gaoler'."""
    t = _strip_color(text).strip()
    t = re.sub(r'\s*souls?\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'^\s*souls?\s+of\s+(the\s+)?', '', t, flags=re.IGNORECASE)
    return t.strip()


def identity_match(monster_text, soul_text):
    """True iff the soul's display name identifies the monster's display name.

    DISPLAY TEXT ONLY - the .dbr filename is never consulted (it is the axis that
    caused the defect: base-game hero .dbr families reuse one filename across
    several differently-named heroes).
    """
    core = _soul_core(soul_text)
    sc, sw = _concat(core), _words(core)
    if not sc:
        return False
    raw = _strip_color(monster_text)
    # A monster name may be "Name ~ Family Epithet"; each side can carry identity.
    # NOTE: '~' is also a legal name character ('~V~', an Iron Lore dev dummy), so
    # the WHOLE string is always a candidate too, and the exact test below runs
    # before any length floor.
    candidates = [seg for seg in raw.split('~') if seg.strip()] + [raw]
    for seg in candidates:
        mc = _concat(seg)
        if not mc:
            continue
        # EXACT identity - no length floor. A short name ('Ino', 'Ben', '~V~')
        # cannot be length-gated out of matching its own soul; an exact equality
        # can never be a false positive, so this only ever removes false NEGATIVES.
        if mc == sc:
            return True
        # partial containment needs a length floor, or 3-letter names start
        # colliding with unrelated souls ('ino' inside 'rhinocerous').
        if len(mc) >= _MIN_CONCAT and len(sc) >= _MIN_CONCAT \
                and (mc in sc or sc in mc):
            return True
        if _words(seg) & sw:
            return True
    return False


# ============================================================================
# db helpers
# ============================================================================
def _scalar(v):
    if isinstance(v, list):
        return v[0] if v else None
    return v


def _chance_of(db, rec):
    try:
        return float(_scalar(db.get_field_value(rec, _CHANCE)) or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _is_soul_carrier(db, name):
    r"""Is this record a SOUL CARRIER - something that can hand the PLAYER a soul?

    The caller has already established that the record holds LIVE soul loot
    (lootFinger2Item1 -> a \soul\ item AND chanceToEquipFinger2 > 0); only
    Monster.tpl-derived records carry those fields at all. So this predicate only
    has to subtract the records that hold those fields without ever dropping
    anything to a player:

      * PETS - record type 'Pet', or a '\pets\' path segment. A pet is spawned by
        the player (monster scrolls, soul summons) and yields no loot; its loot
        fields are inherited clone noise. Counting them is not merely useless, it
        is HARMFUL: the 0.5% monster-scroll pet
        `item\miscellaneous\monsterscrolls\pets\maenad_sorceress_20.dbr` displays
        "Maenad ~ Sorceress", which would crown it rightful OWNER of the Maenad
        Sorceress Soul and convict the real 50% Boss that legitimately drops it
        ('Meritamen the Shadowcaller'). Excluding a record can only ever REMOVE a
        conviction (an excluded owner turns its whole name-group into the
        untouched no-owner case), so this exclusion fails safe by construction.
      * QUEST SPAWN PROXIES / LOOT POOLS - record type 'Proxy' or a '\proxies\'
        path segment. Not creatures; they mirror the boss they spawn.

    DELIBERATELY NOT path-scoped to \creature(s)\. That was the round-1 defect:
    it hid 97 live carriers, including all 25 of records\drxcreatures\ (shipping
    DRX/Urder content) and with them a real mismatch, 'Akara' dropping the
    Kallixenia soul. Any future content module authoring a wire ANYWHERE is now
    judged - which is what "roster-wide" has to mean to be worth claiming.
    """
    nl = str(name).replace('/', '\\').lower()
    if '\\pets\\' in nl or '\\proxies\\' in nl:
        return False
    return db._record_types.get(name, '') not in ('Pet', 'Proxy')


def _soul_family(soul_path):
    r"""'...\ratman\wheedletongue_soul_n.dbr' -> 'ratman\wheedletongue'.

    REPORTING ONLY - never the grouping key (see name_key). The parent directory
    is part of the family because two DIFFERENT soul items can share a basename:
    soul\abyssalliche\kallixenia_soul_* (SV's Liche Queen) and
    soul\svc_uber\kallixenia_soul_* (ours, wired to 'Akara') are distinct items
    with distinct stats. The round-1 basename-only key merged them.
    """
    p = str(soul_path).replace('/', '\\').rstrip('\\').split('\\')
    b = p[-1]
    if b.lower().endswith('.dbr'):
        b = b[:-4]
    b = re.sub(r'_(n|e|l)$', '', b, flags=re.IGNORECASE)
    b = re.sub(r'_soul$', '', b, flags=re.IGNORECASE)
    b = b.lower().strip('_')
    return f"{p[-2].lower()}\\{b}" if len(p) > 1 else b


def name_key(soul_display_text):
    """The GROUPING key: the soul's DISPLAY NAME, normalized.

    Identity is what the player reads. Grouping by the .dbr filename (round 1)
    repeated, inside the gate, the exact filename-is-identity mistake the gate
    exists to punish: it both MERGED two different items that share a basename
    and would SPLIT two items that share a name. '' when the name is unknown.
    """
    return _concat(soul_display_text)


def _soul_refs(db, rec):
    v = db.get_field_value(rec, _LOOT)
    if v is None:
        return []
    vals = v if isinstance(v, list) else [v]
    return [s for s in vals if isinstance(s, str) and 'soul' in s.lower()]


def _display_tags(db, tags):
    """tagKey(lower) -> displayed text, from the mod's authored tags UNION the SV
    0.98i upstream Text_EN (which carries every base-game/SV monster + soul name).

    The SV table is stashed on apply_svc_patches by build_svc_database.main()
    (`_SV098I_NAME_TAGS`), the same module-global hand-off the F6 soul-provenance
    sets use. Fail loud if it is absent: silently resolving nothing would make
    every identity "unknown" and quietly disable the whole gate.
    """
    import apply_svc_patches as asp
    sv = getattr(asp, '_SV098I_NAME_TAGS', None)
    if not sv:
        raise SystemExit(
            "[soul_identity] _SV098I_NAME_TAGS is empty - the SV 0.98i Text_EN "
            "display-name table was not loaded by build_svc_database.main(). "
            "Without it no monster/soul identity can be resolved and this gate "
            "would silently pass. Refusing to ship an unchecked soul roster.")
    out = dict(sv)
    for k, v in (tags or {}).items():
        out[str(k).lower()] = v
    # ── F6 FINAL NAMES (b97r2). apply() runs inside run_registry(), which is
    # BEFORE run_registry_gates() calls _apply_soul_naming_standard() - the
    # documented "final authoritative override of the `tags` dict". verify()
    # runs AFTER it. So round 1's apply() judged identity against names that
    # are NOT the ones the player sees, and could therefore disagree with its
    # own verify(). Real case: tagSVCSoulKallixenia is '{^F}Soul of Kallixenia'
    # at apply() time and '{^F}Kallixenia ~ Liche Queen Soul' in the shipped
    # Text.arc - a different identity, and the difference IS the Akara bug.
    # Applying the same override here makes both passes judge the shipped text.
    # (The companion auto-transform only swaps '{^F}Soul of X' <-> '{^F}X Soul',
    # which _soul_core() normalizes away, so it cannot change an identity.)
    for k, v in getattr(asp, '_SOUL_NAME_STANDARD', {}).items():
        out[str(k).lower()] = v
    return out


def _text_of(tagmap, key):
    return tagmap.get(str(key or '').lower(), '')


# ============================================================================
# the rule
# ============================================================================
def soul_display_map(db, tagmap):
    r"""soul item record (lower, backslashes) -> its displayed name."""
    out = {}
    for name in db.record_names():
        nl = name.replace('/', '\\').lower()
        if '\\soul\\' not in nl:
            continue
        t = _scalar(db.get_field_value(name, 'itemNameTag'))
        if t:
            txt = _text_of(tagmap, t)
            if txt:
                out[nl] = txt
    return out


def live_carriers(db):
    """Yield (record, [soul item refs]) for every LIVE soul carrier, roster-wide."""
    for name in db.record_names():
        refs = _soul_refs(db, name)
        if not refs or _chance_of(db, name) <= 0:
            continue
        if not _is_soul_carrier(db, name):
            continue
        yield name, refs


def find_identity_thieves(db, tags):
    """Apply THE RULE. Returns (thieves, groups).

    thieves: {record -> (monster_display, soul_display_name, owner_display)}
    groups:  {name_key -> {'display': soul name, 'souls': {item refs},
                           'families': {file families}, 'matched': [(rec, disp)],
                           'unmatched': [(rec, disp)]}}
    """
    tagmap = _display_tags(db, tags)
    soul_display = soul_display_map(db, tagmap)

    groups = {}
    unresolved = []
    for name, refs in live_carriers(db):
        disp = _text_of(tagmap, _scalar(db.get_field_value(name, 'description')))
        seen = set()
        for ref in refs:
            sd = soul_display.get(ref.replace('/', '\\').lower(), '')
            key = name_key(sd)
            # UNJUDGEABLE -> SKIP, never "unmatched". If either side's display
            # name does not resolve, this carrier's identity is UNKNOWN, and an
            # unknown identity must never be convicted of theft (that would zero
            # a real drop over a missing Text tag). Skipping also keeps it out of
            # 'matched', so it cannot vouch for a name either.
            if not key:
                unresolved.append((name, ref))
                continue
            e = groups.setdefault(key, {'display': sd, 'souls': set(),
                                        'families': set(),
                                        'matched': [], 'unmatched': []})
            e['souls'].add(ref)
            e['families'].add(_soul_family(ref))
            if key in seen:
                continue          # same soul NAME reached via several tiers
            seen.add(key)
            if not disp:
                unresolved.append((name, ref))
                continue
            e['matched' if identity_match(disp, sd) else 'unmatched'].append(
                (name, disp))
    find_identity_thieves.last_unresolved = unresolved

    # A record that OWNS some soul must never be zeroed for carrying another: the
    # write is per-RECORD (one chanceToEquipFinger2), so zeroing it would also kill
    # its legitimate drop. No record in the current roster carries two soul names,
    # but the rule must be safe if one ever does.
    owners = {rec for e in groups.values() for rec, _d in e['matched']}

    thieves = {}
    for _key, e in groups.items():
        if not e['matched'] or not e['unmatched']:
            # nobody owns the name (archetype / name-drift / mod-themed), or every
            # carrier owns it (difficulty variants). Either way: hands off.
            continue
        owner = e['matched'][0][1]
        for rec, disp in e['unmatched']:
            if rec in owners:
                continue  # owns a different soul; detaching would kill that too
            thieves[rec] = (disp, _strip_color(e['display']), owner)
    return thieves, groups


# ============================================================================
# apply / verify
# ============================================================================
def apply(db, tags):
    print(f"\n=== patches-registry: {MODULE_NAME} ===")
    thieves, groups = find_identity_thieves(db, tags)

    carriers = {r for e in groups.values()
                for b in ('matched', 'unmatched') for r, _d in e[b]}
    shared_ok = sum(1 for e in groups.values() if not e['matched'])
    print(f"  judged {len(carriers)} live soul carrier(s) roster-wide (every path, "
          f"pets + quest proxies excluded) across {len(groups)} distinct soul "
          f"NAME(s); {shared_ok} name(s) have NO identity-owning carrier "
          f"(archetype / name-drift / mod-themed) and are untouched by construction")
    unresolved = getattr(find_identity_thieves, 'last_unresolved', [])
    if unresolved:
        print(f"  {len(set(r for r, _f in unresolved))} carrier(s) SKIPPED as "
              f"unjudgeable (monster or soul display name does not resolve; an "
              f"unknown identity is never convicted): "
              f"{sorted({r for r, _f in unresolved})[:5]}")

    # ── REVIEW GATE: the rule's verdict must be the reviewed verdict ─────────
    got = {k.replace('/', '\\').lower() for k in thieves}
    want = {k.lower() for k in _REVIEWED}
    if got != want:
        added = sorted(got - want)
        gone = sorted(want - got)
        raise SystemExit(
            "[soul_identity] REVIEW GATE: the identity rule's verdict no longer "
            "matches the set classified in the b97 audit. This is not "
            "automatically a bug - new content can legitimately move it - but a "
            "soul drop must never be zeroed (or silently un-zeroed) without a "
            "human classifying it. Re-run the audit, update _REVIEWED and "
            "docs/reports/b97_soul_identity_audit.md.\n"
            f"  NEWLY flagged as identity thieves ({len(added)}): {added}\n"
            f"  NO LONGER flagged ({len(gone)}): {gone}")

    # what each thief was the LAST live carrier of, measured BEFORE the write
    live_before = {}
    for rec, refs in live_carriers(db):
        for ref in refs:
            live_before.setdefault(ref.replace('/', '\\').lower(), set()).add(rec)

    zeroed = 0
    for rec in sorted(thieves, key=lambda r: r.lower()):
        disp, soul_name, owner = thieves[rec]
        prev = _chance_of(db, rec)
        # DOWNWARD ONLY, single field. lootFinger2Item1 is left intact on purpose
        # (detach the roll, keep the data - the A4 Aphiastas-zero / R-45
        # tombguardian shape), so the change stays reviewable and reversible.
        db.set_field(rec, _CHANCE, 0.0, DATA_TYPE_FLOAT)
        db._modified.add(rec)
        zeroed += 1
        print(f"  ZEROED {prev:g}% -> 0%  {disp!r} ({rec}) was dropping "
              f"{soul_name!r}, which belongs to {owner!r}")

    # ── ITEM-DETACH GUARD: no soul ITEM goes dark without a reviewed waiver ──
    # The ORPHAN PROOF below is about the soul NAME (is it still obtainable?).
    # This is about the specific ITEM RECORD: two distinct items can share one
    # display name, so zeroing a thief can leave a real, authored item with no
    # live carrier at all while the NAME looks fine. That is content going dark
    # and must never be silent.
    orphaned_items = sorted(
        ref for ref, recs in live_before.items()
        if recs and all(_chance_of(db, r) <= 0 for r in recs))
    unreviewed = [r for r in orphaned_items
                  if r not in {k.lower() for k in _ACCEPTED_ITEM_DETACH}]
    if unreviewed:
        raise SystemExit(
            "[soul_identity] ITEM-DETACH GUARD: zeroing the identity thieves "
            "would leave these soul ITEM records with NO live carrier anywhere "
            "(the item becomes undroppable even if its display NAME is still "
            "obtainable from another item). That is content going dark - review "
            "it and either re-point the wire or add a justified entry to "
            f"_ACCEPTED_ITEM_DETACH:\n  - " + "\n  - ".join(unreviewed))
    for ref in orphaned_items:
        print(f"  NOTE item now undroppable (reviewed waiver, record kept): {ref}")

    # ── ORPHAN PROOF: every zeroed soul NAME still has a live rightful owner ──
    for key in sorted({name_key(f) for _d, f, _o in thieves.values()}):
        live_owners = [d for r, d in groups[key]['matched']
                       if _chance_of(db, r) > 0]
        if not live_owners:
            raise SystemExit(
                f"[soul_identity] ORPHAN GUARD: zeroing the identity thieves of "
                f"soul {groups[key]['display']!r} would leave it with NO live "
                f"carrier - the soul would become unobtainable. Refusing (the "
                f"rule requires a matching carrier to exist; something zeroed "
                f"the owner after the classification).")
    print(f"  {zeroed} identity thief record(s) detached from their foreign soul; "
          f"every affected soul name still drops from its rightful owner")


def verify(db, tags):
    r"""Step-4 permanent regression gate over the FINAL merged db (post gate
    battery, post drop-rate forcer). LIST-FREE: it re-runs the rule and requires
    the answer to be empty. A future clone/wire that hands a creature another
    named creature's soul fails the build here - ANY path, not just
    \creature(s)\ (records\drxcreatures\ and records\test\ are shipping content
    and are judged too; see _is_soul_carrier)."""
    thieves, _groups = find_identity_thieves(db, tags)
    if thieves:
        lines = [f"{d!r} ({r}) drops {f!r}, which belongs to {o!r}"
                 for r, (d, f, o) in sorted(thieves.items(), key=lambda kv: kv[0].lower())]
        raise SystemExit(
            "[soul_identity] VERIFY FAILED (Will 2026-07-27: \"some of the heroes "
            "are dropping the wrong souls or souls for other boss monsters\"): "
            f"{len(thieves)} creature(s) still drop a soul whose identity belongs "
            "to a DIFFERENT named creature that also drops it:\n  - "
            + "\n  - ".join(lines))
    print("  [soul_identity] verify OK: no creature drops another named "
          "creature's soul (identity checked on display names, every record "
          "path, pets + quest proxies excluded)")
