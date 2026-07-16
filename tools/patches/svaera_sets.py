r"""svaera_sets - re-link the 5 SVAERA Greek/Egyptian item sets (SVAERA-ADOPT).

WHY THIS EXISTS (docs/BACKLOG.md "SVAERA-ADOPT", 2026-07-14, verifier-corrected)
--------------------------------------------------------------------------------
The SVAERA-goodies audit (docs/reports/svaera_goodies_audit.md) found 5 clean
Greek/Egyptian item sets SVAERA authors additively over stock SV098i content:

    drxset049  Thoth's Favor              (2 members, Egyptian)
    drxset051  Hector's Bronze Armor      (3 members, Greek/Trojan)
    drxset052  Robes of the Pythia        (2 members, Greek/Delphi)
    drxset053  Patroclus' Disguise        (3 members, Greek/Trojan)
    drxset058  Might of Hephaestus        (3 members, Greek/smith-god)

The verifier's correction (2026-07-14) narrowed the adoption recipe: the 13
member ITEMS are **not absent** - every one already ships in our mod today
(itemset.tpl-independent unique items, present since the SV098i merge), just
with no `itemSetName` linking them into a set. Only the 5 SET-GROUPING records
themselves are missing.

GIT-BLAME GATE (per the round-1 brief - "first git-log/blame WHERE our build
stripped itemSetName from the 13 items; if the strip was an explicit
intentional decision, STOP item 1 and report")
--------------------------------------------------------------------------------
Ground-truthed directly against the arz sources (no history to blame - this
was never a removal):
  - `git log --all -S itemSetName -- tools/` and `-S drxset0` turn up NO commit
    that ever authored, touched, or stripped these 13 items or these 5 set
    records. Nothing in our own tooling references them at all.
  - The 13 member items are present, byte-for-byte structurally consistent,
    in ALL THREE upstream sources we merge (`upstream/soulvizier_098i`,
    `_0.9`, `_041`) as their own SV098i-original standalone-unique records -
    and in every one of those, the record NEVER carries an `itemSetName`
    field (not "present but empty" - the field key itself is absent from the
    dbr). So there was nothing to strip: these items shipped from SV098i as
    standalone uniques from day one; itemSetName is not a field our pipeline
    removes, it is a field amgoz1's SV098i originals never had.
  - The 5 drxset0{49,51,52,53,58}.dbr grouping records are ALSO absent from
    all three upstream sources - they are SVAERA's own additive invention
    (SVAERA repackaged pre-existing SV098i uniques into new sets). Since we
    never grafted SVAERA's `records\item\sets\` namespace, the grouping
    record simply never arrived; the member items arrived on their own via
    the ordinary upstream merge.
CONCLUSION: NOT an intentional strip - there is no prior decision to reverse.
Proceeding with authoring the recipe below (verifier's smaller re-link), per
the brief's else-branch.

TIER RECONCILIATION (why this module does NOT touch itemClassification)
--------------------------------------------------------------------------------
A few members were independently re-tiered by our own build vs. SVAERA's
copy (ground-truthed): SVAERA's Hector's Spear ships Epic (`u_e_...`) while
OUR copy of the very same record is Legendary; the other 12 members' tiers
match SVAERA's own (Thoth/Achilles/Hephaestus pieces Legendary, Pythia pieces
Epic - `um_e_...`). A set-grouping record only stores `setMembers` (item PATH
refs) and flat set-bonus stats; it does not encode or require any particular
member itemClassification, so re-tiering is orthogonal and untouched here.

WHAT THIS MODULE DOES
--------------------------------------------------------------------------------
For each of the 5 sets: creates `records\\item\\sets\\drxset0NN.dbr` (bare
`_ensure_record`, `database\\Templates\\ItemSet.tpl` - the exact template our
own drxset001-047 family already uses), with:
  - the exact per-piece set-bonus fields SVAERA ships (ground-truthed field
    name + dtype + value array from the live SVAERA arz - the amgoz1/SVAERA
    design is PORTED VERBATIM, never re-balanced),
  - `setMembers` pointing at OUR 13 items (exact stored paths, confirmed
    present),
  - `setName` -> a FRESH tag `tagSetName0NN`, following the EXACT numbering
    convention our own non-xpack `records\\item\\sets\\drxset001..047.dbr`
    family already uses (`tagSetName001`..`tagSetName047`; the xpack family
    uses the parallel `xtagSetName0NN`). This is a clean, collision-free
    continuation of our own established pattern (048-058 unused before this
    module) - simpler and safer than porting SVAERA's own unrelated tag keys
    (`tagSetNameLE1/3/5/6`, `xtagArtifactDescription062`), which follow a
    different, non-contiguous SVAERA-internal numbering scheme.
Then sets `itemSetName` on each of the 13 member items to its set's path (the
one field genuinely missing - the actual "re-link").

Text tag values (`tags[...]`) are the SVAERA-authored set names, ground-truthed
directly from the live SVAERA `Text.arc` (Thoth's Favor / Hector's Bronze
Armor / Robes of the Pythia / Patroclus' Disguise / Might of Hephaestus) -
amgoz1-era names, unmodified.

NO new art, no loot-table changes, no map changes (Tier-1 sets ship with art
already shipped; the 13 items are already droppable via our existing loot
tables - this module only adds the grouping + linking data), consistent with
the efficiency law (S effort, per the audit).
"""

MODULE_NAME = "SVAERA 5-set re-link (Thoth/Hector/Pythia/Patroclus/Hephaestus)"

DATA_TYPE_FLOAT = 1
DATA_TYPE_STRING = 2

_SET_TEMPLATE = 'database\\Templates\\ItemSet.tpl'

# Each entry: (drxset NN, path, our tag key, SVAERA-ground-truthed name,
#              FileDescription (dev label, mirrors SVAERA's own),
#              [(field, dtype, values), ...] set-bonus fields verbatim from
#              SVAERA, setMembers (OUR exact stored item paths)).
_SETS = [
    dict(
        num='049',
        path=r'records\item\sets\drxset049.dbr',
        tag='tagSetName049',
        name="Thoth's Favor",
        desc='LE Thoth - 50% vit+bleedres',
        bonuses=[
            ('characterBaseAttackSpeedTag', DATA_TYPE_STRING, ['CharacterAttackSpeedAverage']),
            ('defensiveBleeding', DATA_TYPE_FLOAT, [0.0, 50.0]),
            ('defensivePoison', DATA_TYPE_FLOAT, [0.0, 50.0]),
            ('offensiveSlowFireDurationMin', DATA_TYPE_FLOAT, [0.0, 3.0]),
            ('offensiveSlowFireMin', DATA_TYPE_FLOAT, [0.0, 20.0]),
            ('offensiveSlowPoisonDurationMin', DATA_TYPE_FLOAT, [0.0, 3.0]),
            ('offensiveSlowPoisonMin', DATA_TYPE_FLOAT, [0.0, 20.0]),
        ],
        members=[
            r"records\item\equipmentring\u_e_thoth'smark.dbr",
            r"records\item\equipmentarmor\u_l_thoth'sshadow.dbr",
        ],
    ),
    dict(
        num='051',
        path=r'records\item\sets\drxset051.dbr',
        tag='tagSetName051',
        name="Hector's Bronze Armor",
        desc='LE Hector - attspeed & eleres',
        bonuses=[
            ('characterAttackSpeedModifier', DATA_TYPE_FLOAT, [0.0, 12.0, 24.0]),
            ('characterBaseAttackSpeedTag', DATA_TYPE_STRING, ['CharacterAttackSpeedAverage']),
            ('defensiveElementalResistance', DATA_TYPE_FLOAT, [0.0, 12.0, 24.0]),
        ],
        members=[
            r"records\item\equipmenthelm\u_l_hector'sflashinghelm.dbr",
            r'records\item\equipmentshield\u_l_hectorsshimmeringshield.dbr',
            r"records\item\equipmentweapon\spear\u_e_hector'sspear.dbr",
        ],
    ),
    dict(
        num='052',
        path=r'records\item\sets\drxset052.dbr',
        tag='tagSetName052',
        name='Robes of the Pythia',
        desc='LE Pythia - int% & castspeed',
        bonuses=[
            ('characterBaseAttackSpeedTag', DATA_TYPE_STRING, ['CharacterAttackSpeedAverage']),
            ('characterIntelligenceModifier', DATA_TYPE_FLOAT, [0.0, 20.0]),
            ('characterSpellCastSpeedModifier', DATA_TYPE_FLOAT, [0.0, 20.0]),
        ],
        members=[
            r"records\item\equipmentarmor\um_e_pythia'svestment.dbr",
            r"records\item\equipmentarmband\um_e_pythia'sclasp.dbr",
        ],
    ),
    dict(
        num='053',
        path=r'records\item\sets\drxset053.dbr',
        tag='tagSetName053',
        name="Patroclus' Disguise",
        desc='LE Achilles - health% & eleres',
        bonuses=[
            ('characterBaseAttackSpeedTag', DATA_TYPE_STRING, ['CharacterAttackSpeedAverage']),
            ('characterLifeModifier', DATA_TYPE_FLOAT, [0.0, 18.0, 18.0]),
            ('defensiveElementalResistance', DATA_TYPE_FLOAT, [0.0, 0.0, 25.0]),
        ],
        members=[
            r'records\item\equipmentarmor\u_l_armorofachilles.dbr',
            r"records\item\equipmentweapon\spear\u_l_achilles'spear.dbr",
            r"records\item\equipmentshield\u_l_achilles'shield.dbr",
        ],
    ),
    dict(
        num='058',
        path=r'records\item\sets\drxset058.dbr',
        tag='tagSetName058',
        name='Might of Hephaestus',
        desc='LE Hephaestus',
        bonuses=[
            ('characterBaseAttackSpeedTag', DATA_TYPE_STRING, ['CharacterAttackSpeedAverage']),
            ('characterDefensiveBlockRecoveryReduction', DATA_TYPE_FLOAT, [0.0, 0.0, 15.0]),
            ('defensivePierce', DATA_TYPE_FLOAT, [0.0, 20.0, 40.0]),
            ('defensiveProtectionModifier', DATA_TYPE_FLOAT, [0.0, 0.0, 10.0]),
        ],
        members=[
            r'records\item\equipmentweapon\club\u_l_handofhephaestus.dbr',
            r"records\item\equipmentshield\u_l_hephaestus'moltenshield.dbr",
            r'records\item\equipmentring\u_l_sealofhephaestus.dbr',
        ],
    ),
]


def _norm(p):
    return str(p).replace('/', '\\').lower()


def apply(db, tags):
    from apply_svc_patches import _ensure_record

    name_by_norm = {_norm(n): n for n in db.record_names()}
    created = []
    linked = []

    for s in _SETS:
        path = s['path']
        if db.has_record(path):
            raise SystemExit(
                "svaera_sets: %s already exists - refusing to overwrite an "
                "existing set record" % path)

        # Resolve every member to its EXACT stored name (case/apostrophe-exact)
        # and fail loud if any of the 13 items is missing - this module never
        # silently ships a partial set.
        resolved_members = []
        for m in s['members']:
            hit = name_by_norm.get(_norm(m))
            if not hit:
                raise SystemExit(
                    "svaera_sets: expected member item missing from the DB: "
                    "%s (set %s / %s)" % (m, s['path'], s['name']))
            resolved_members.append(hit)

        _ensure_record(db, path, _SET_TEMPLATE)
        db.set_field(path, 'FileDescription', s['desc'], DATA_TYPE_STRING)
        for field, dtype, values in s['bonuses']:
            db.set_field(path, field, values, dtype)
        db.set_field(path, 'setMembers', resolved_members, DATA_TYPE_STRING)
        db.set_field(path, 'setName', s['tag'], DATA_TYPE_STRING)
        db._modified.add(path)
        created.append(path)

        tags[s['tag']] = s['name']

        for member in resolved_members:
            db.set_field(member, 'itemSetName', path, DATA_TYPE_STRING)
            db._modified.add(member)
            linked.append(member)

    print("  svaera_sets: authored %d set record(s): %s"
          % (len(created), [p.rsplit('\\', 1)[-1] for p in created]))
    print("  svaera_sets: re-linked itemSetName on %d member item(s)"
          % len(linked))


def verify(db, tags):
    """POST-FINALIZATION invariant (fail-loud):
      - all 5 set records exist, each with a non-empty setMembers list whose
        every ref resolves in the db and whose itemSetName points back at the
        set;
      - each set's Text tag resolves in `tags`;
      - member count matches the 2/3/2/3/3 recipe exactly (13 total)."""
    total_members = 0
    for s in _SETS:
        path = s['path']
        if not db.has_record(path):
            raise SystemExit("svaera_sets.verify FAIL: set record missing: %s" % path)
        members = db.get_field_value(path, 'setMembers')
        members = members if isinstance(members, list) else ([members] if members else [])
        if len(members) != len(s['members']):
            raise SystemExit(
                "svaera_sets.verify FAIL: %s has %d setMembers, expected %d"
                % (path, len(members), len(s['members'])))
        for m in members:
            if not db.has_record(m):
                raise SystemExit(
                    "svaera_sets.verify FAIL: %s setMembers ref does not "
                    "resolve: %s" % (path, m))
            back = db.get_field_value(m, 'itemSetName')
            back = back[0] if isinstance(back, list) and back else back
            if _norm(back) != _norm(path):
                raise SystemExit(
                    "svaera_sets.verify FAIL: %s itemSetName=%r does not "
                    "point back at %s" % (m, back, path))
        set_tag = db.get_field_value(path, 'setName')
        set_tag = set_tag[0] if isinstance(set_tag, list) and set_tag else set_tag
        if set_tag != s['tag']:
            raise SystemExit(
                "svaera_sets.verify FAIL: %s setName=%r != expected tag %r"
                % (path, set_tag, s['tag']))
        if tags.get(s['tag']) != s['name']:
            raise SystemExit(
                "svaera_sets.verify FAIL: tag %s missing/wrong in Text tags "
                "(got %r, expected %r)" % (s['tag'], tags.get(s['tag']), s['name']))
        total_members += len(members)

    if total_members != 13:
        raise SystemExit(
            "svaera_sets.verify FAIL: total member count %d != 13"
            % total_members)

    print("  svaera_sets.verify OK: 5/5 sets present, 13/13 members linked "
          "+ round-trip itemSetName verified, 5/5 tags resolve.")
