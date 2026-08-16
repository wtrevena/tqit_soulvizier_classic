r"""build_shroud_rig - the Enslaver's OWN smoking rig, byte-derived from the one
mesh Will has personally confirmed smokes in play (R-257).

--------------------------------------------------------------------------------
WHY A NEW ASSET EXISTS AT ALL - FIVE FILINGS, FOUR OF THEM IN THE RECORD LAYER
--------------------------------------------------------------------------------
Will has now asked five times for the Enslaver to wear "the same black shadow
shroud his demon summon guys have". Rounds 1-4 all worked in the `.dbr` FIELD
layer, all verified themselves at the record level, and all failed in game:

  b39/b55/b55r2/b92  charFxPakRunningNames / weapon-bone paks - never rendered
  b93 (R-250)        skillName18/19 - slots MonsterSkillManager.tpl does not declare
  b99 (R-255)        initialSkillName + buffSelfSkillName - declared, byte-verified,
                     gate-verified, and STILL nothing on screen (Will's 08-15
                     screenshot: summoned Enslaver at Hathor Basin, DEV post-b100,
                     zero smoke, standing out of combat)

The census that closed it (R-257): across all 341 vanilla Pets, the exact b99
shape - Pet + an always-on channel + a `Skill_BuffSelfToggled` + a body-attach
CharFxPak - occurs **zero** times, and `ShadowStalker_Smoke.dbr` is referenced 13
times in the entire base game, every one of them a `deathEffect`. Its ONLY
persistent rendering anywhere on earth is the block compiled into a `.msh`.

So this lane does not add a fifth channel. It replicates the ONE mechanism with a
confirmed rendering exemplar, byte for byte.

--------------------------------------------------------------------------------
THE EXEMPLAR, AND WHY IT IS THE STANDARD
--------------------------------------------------------------------------------
`Creatures\Monster\ShadowStalker\ShadowStalker.msh` (base `Resources\Creatures.arc`,
337,825 B) ends in exactly this, read out of the binary:

    CreateEntity\r\n{\r\n    attach = "SpecialHit01"\r\n
        entity = "Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr"\r\n}\r\n

Three independent witnesses that it RENDERS:

  1. WILL CONFIRMED IT BY EYE. R-102 fourth amendment, verbatim: "yes the demons
     that he summons have the proper black shroud and they dont have any green".
     The wearers are `um_enslaver_marauder_99` + `enslaver_marauder_1/2/3`, all on
     this exact mesh, all with `initialSkillName = buffSelfSkillName = None` in the
     shipped arz. Nothing but the mesh can be producing that smoke.
  2. BASE-GAME UBIQUITY. 28 vanilla records wear this mesh (the Act 2 shadow
     stalker family). 66 of 591 distinct vanilla creature meshes carry a
     CreateEntity FX block; it is how the base game does ambient auras.
  3. IT IS THE ONLY MECHANISM THAT SHIPS ON `Pet.tpl`. Every vanilla player pet
     with a persistent ambient aura is mesh-driven with EMPTY always-on fields:
     Ancestral Warriors, the Spirit Outsider, Storm Wisps, Spirit Ward, Battle
     Standard.

--------------------------------------------------------------------------------
THE TRANSFORMATION, AND WHY IT IS SAFE (measured in both binaries)
--------------------------------------------------------------------------------
A `.msh` is a self-describing CHUNK CHAIN with NO global offset table:

    'MSH' + version byte + u32, then [u32 chunk_id][u32 chunk_len][payload] ...

Measured: ShadowStalker.msh and SkeletonGrayBlack01New.msh both walk to
**EOF-exact in 9 chunks**, and in both the LAST chunk is id 3 - the CRLF text
section that carries `AttachPoint{...}`, the joint table and (on the exemplar)
the `CreateEntity` block. Exactly ONE u32 anywhere in either file equals that
chunk's length, and none equals the file length, so there is no second size to
keep in sync.

The edit is therefore the format's own append: copy the donor, put the exemplar's
CreateEntity bytes on the end of chunk 3, add their length to chunk 3's length
u32. Every other byte is untouched, and `verify()` re-derives all of it:

    A1  the appended bytes are byte-identical to the exemplar's own final block,
        re-read from ShadowStalker.msh every run
    A2  every byte before chunk 3's length field is identical to the donor
    A3  the donor's own text chunk is preserved verbatim, appended to and not
        rewritten
    A4  the rig walks to EOF-exact, same 9 chunk ids in the same order, and ONLY
        chunk 3's length differs (by exactly len(block))
    A5  `rig_names_of()` is IDENTICAL to the donor's 31 names - the animation
        surface is untouched by construction, which is the risk R-102's fourth
        amendment names as the real one in any rig change
    A6  the attach point the block names is declared on the donor's own rig
    A7  the donor carries NO embedded FX, so the block we add is the only one
    A8  len(rig) == len(donor) + len(block)

--------------------------------------------------------------------------------
WHERE IT SHIPS, AND WHY THAT PATH IS PROVEN
--------------------------------------------------------------------------------
Into the mod's own `Resources\Creatures.arc` under a NET-NEW name. Measured:

  * The mod's Creatures.arc already ships 288 entries and shadows **zero** base
    entries - including two net-new `.msh` (`pc/female/female1.msh`,
    `pc/female/female2.msh`) that serve a live record. Same archive, same asset
    type, same net-new-name shape as this rig.
  * The engine unions same-named archives PER ENTRY, and the proof is the game
    Will plays: the mod ships that Creatures.arc today and every base-game
    creature still renders - the Enslaver himself is standing on a BASE-arc mesh
    in the 08-15 screenshot.
  * 1,105 of the mod's Monster/Pet records already resolve their `mesh` out of a
    MOD-shipped archive (739 `DRX.arc`, 345 `SVMesh.arc`, 20 `_DRX_Meshes.arc`),
    and Will has confirmed those render (`DRX\meshes\blooddemon01.msh` is the
    Devourer's blood demons).

A NEW name rather than shadowing `monster/skeleton/skeletongrayblack01new.msh`:
mod-over-base shadowing of a mesh is UNPROVEN on this rig, and it must not become
the load-bearing assumption of a fifth attempt.

⚠️ DEPLOY COUPLING (new with R-257, and it is a P0 if missed): this lane is the
first to make a `.dbr` depend on a MOD-SHIPPED ART asset. `work\<mod>\Resources\
Creatures.arc` must be REBUILT and DEPLOYED in the same ship as the arz, or the
Enslaver family resolves no mesh at all. `enslaver_shroud.verify()` arm M2 fails
the build loud whenever a mod Creatures.arc is reachable and does not carry the
rig, which is exactly the "operator forgot to restage" case.

CLI:
    py tools/build_shroud_rig.py --check                  # derive + verify, write nothing
    py tools/build_shroud_rig.py --out <path.msh>         # write the rig alone
    py tools/build_shroud_rig.py --selftest               # re-measure the load-bearing facts
    py tools/build_shroud_rig.py --negtest                # planted corruptions must all RED
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import mesh_assets                                                   # noqa: E402
from arc_patcher import ArcArchive                                   # noqa: E402

# ── the three assets ────────────────────────────────────────────────────────
# The donor: the Enslaver's CURRENT rig (champion_mesh / R-102 put him on it to
# kill the green). His silhouette is R-102's deliberate design and this lane does
# not trade it away, which is the whole reason a new asset exists instead of a
# plain swap onto ShadowStalker.msh.
DONOR_MESH = r'Creatures\Monster\Skeleton\SkeletonGrayBlack01New.msh'
# The exemplar: the ONLY confirmed-rendering instance of this effect in the
# project (Will, by eye, R-102 fourth amendment).
EXEMPLAR_MESH = r'Creatures\Monster\ShadowStalker\ShadowStalker.msh'
# What we author. `Creatures` is the ARCHIVE name, `monster\skeleton\...` the
# entry inside it (the addressing pitfall mesh_assets documents).
SHROUD_RIG = r'Creatures\Monster\Skeleton\svc_enslaver_shroudrig01.msh'
# Raw entry name, matching the base archive's own convention exactly: lowercase,
# forward slashes (measured: `monster/skeleton/skeletongrayblack01new.msh`).
SHROUD_RIG_ENTRY = 'monster/skeleton/svc_enslaver_shroudrig01.msh'

# The effect the exemplar's block names, and the attach point it hangs it on.
# Both are DERIVED from the binary at build time; these literals exist so the
# constant is readable and so `--negtest` has something to plant against.
DEMON_FX_REF = r'Records\Effects\MonsterFX\ShadowStalker_Smoke.dbr'
DEMON_ATTACH = 'SpecialHit01'

MSH_MAGIC = b'MSH'
TEXT_CHUNK_ID = 3          # the trailing CRLF text section (AttachPoints, joints, FX)
_CHUNK_HDR = 8             # [u32 id][u32 len]
_FILE_HDR = 8              # 'MSH' + version byte + u32


class RigError(SystemExit):
    pass


# ── format ──────────────────────────────────────────────────────────────────

def chunks(data):
    """[(offset_of_header, chunk_id, payload_len)] for a .msh blob.

    Raises RigError unless the chain walks to EOF EXACTLY. That exactness is the
    whole safety argument for appending: a format with a global offset table
    would not walk cleanly after an in-place length bump, and this would say so.
    """
    if data[:3] != MSH_MAGIC:
        raise RigError('not a .msh: magic is %r, expected %r' % (data[:3], MSH_MAGIC))
    off, out = _FILE_HDR, []
    while off + _CHUNK_HDR <= len(data):
        cid, ln = struct.unpack_from('<II', data, off)
        if ln > len(data) - (off + _CHUNK_HDR):
            raise RigError('chunk id=%d len=%d at offset %d overruns the file (%d bytes)'
                           % (cid, ln, off, len(data)))
        out.append((off, cid, ln))
        off += _CHUNK_HDR + ln
    if off != len(data):
        raise RigError('chunk chain ends at %d but the file is %d bytes - this is '
                       'NOT a plain chunk chain and must not be appended to'
                       % (off, len(data)))
    return out


def text_chunk(data):
    """(header_offset, payload_offset, payload_len) of the trailing text chunk.

    It must be the LAST chunk: appending to a chunk that is not last would move
    every byte after it, which is not the edit this module is allowed to make.
    """
    cs = chunks(data)
    if not cs:
        raise RigError('no chunks at all')
    off, cid, ln = cs[-1]
    if cid != TEXT_CHUNK_ID:
        raise RigError('the LAST chunk is id=%d, not the text chunk id=%d - refusing '
                       'to append' % (cid, TEXT_CHUNK_ID))
    return off, off + _CHUNK_HDR, ln


def exemplar_block(exemplar):
    """The exemplar's own final `CreateEntity{...}` bytes, VERBATIM, to EOF.

    Derived, never transcribed. A hand-typed block would be a belief; these are
    the bytes off the disk of the mesh Will watched smoke.
    """
    i = exemplar.rfind(b'CreateEntity')
    if i < 0:
        raise RigError('%s carries no CreateEntity block - the exemplar this whole '
                       'lane copies has changed' % EXEMPLAR_MESH)
    blk = exemplar[i:]
    if b'CreateEntity' in blk[len(b'CreateEntity'):]:
        raise RigError('more than one trailing CreateEntity block - ambiguous')
    if not blk.rstrip().endswith(b'}'):
        raise RigError('the trailing CreateEntity block does not close at EOF: %r'
                       % blk[-40:])
    return blk


# ── read the two BASE binaries (never through the mod chain) ─────────────────

def _base_creatures_path():
    p = Path(mesh_assets.game_dir()) / 'Resources' / 'Creatures.arc'
    if not p.exists():
        raise RigError('base Creatures.arc not found at %s (set SVC_TQAE_DIR)' % p)
    return p


_BASE_ARC = {}


def read_base(ref):
    r"""Bytes of a BASE-GAME creature asset, read straight out of the game's own
    `Resources\Creatures.arc`.

    Deliberately NOT `mesh_assets.read_asset`: that walks the mod archives first,
    and the derivation must be pinned to the pristine base binaries. A mod copy
    feeding its own derivation is how a build becomes non-reproducible and how a
    self-referential rig could be minted from an already-patched one.
    """
    p = _base_creatures_path()
    key = str(p)
    if key not in _BASE_ARC:
        _BASE_ARC[key] = ArcArchive.from_file(p)
    arc = _BASE_ARC[key]
    _name, inner = mesh_assets.split_ref(ref)
    for e in arc.entries:
        if getattr(e, 'entry_type', 3) == 3 and \
                e.name.lower().replace('\\', '/') == inner.replace('\\', '/'):
            return arc.get_file(e.name)
    raise RigError('%s is not in %s' % (ref, p))


# ── derive ──────────────────────────────────────────────────────────────────

def derive(donor, exemplar):
    """The rig bytes: donor + the exemplar's block, chunk-3 length bumped."""
    blk = exemplar_block(exemplar)
    hdr_off, pay_off, ln = text_chunk(donor)
    out = bytearray(donor)
    out[hdr_off + 4:hdr_off + 8] = struct.pack('<I', ln + len(blk))
    out.extend(blk)
    return bytes(out)


def build():
    """(rig_bytes, donor_bytes, exemplar_bytes) from the base game."""
    donor = read_base(DONOR_MESH)
    exemplar = read_base(EXEMPLAR_MESH)
    return derive(donor, exemplar), donor, exemplar


_REF_EXT = ('.ssh', '.tex', '.msh', '.anm', '.pfx', '.dbr', '.mif')


def _embedded_refs(data):
    """Every art/shader/record reference a .msh blob names, in any namespace.

    This is the input to A9: `validate_render_chain` (build30/D5) resolves exactly
    these, and a change here is the difference between a pet that renders and one
    that spawns invisible.
    """
    import re
    out = []
    for s in re.findall(rb'[ -~]{4,}', data):
        t = s.decode('ascii', 'replace')
        for piece in re.split(r'[";=\s]+', t):
            if piece.lower().endswith(_REF_EXT):
                out.append(piece)
    return out


# ── verify (A1..A9; every arm re-derived, none asserted) ────────────────────

def verify_rig(rig, donor, exemplar):
    """[] when the rig is exactly 'the donor plus the exemplar's own block'."""
    problems = []
    blk = exemplar_block(exemplar)
    try:
        d_hdr, d_pay, d_len = text_chunk(donor)
    except RigError as e:
        return ['donor: %s' % e]

    # A8 - size
    if len(rig) != len(donor) + len(blk):
        problems.append('A8 size: rig is %d bytes, donor %d + block %d = %d'
                        % (len(rig), len(donor), len(blk), len(donor) + len(blk)))

    # A2 - everything before the length field is untouched
    if rig[:d_hdr + 4] != donor[:d_hdr + 4]:
        problems.append('A2 prefix: the %d bytes before the text-chunk length field '
                        'differ from the donor' % (d_hdr + 4))

    # A4 - the chunk chain still walks, same shape, only chunk 3 longer
    try:
        rc, dc = chunks(rig), chunks(donor)
    except RigError as e:
        problems.append('A4 chain: %s' % e)
        rc = dc = None
    if rc is not None:
        if [c[1] for c in rc] != [c[1] for c in dc]:
            problems.append('A4 chain: chunk ids changed %r -> %r'
                            % ([c[1] for c in dc], [c[1] for c in rc]))
        else:
            for (ro, rid, rln), (_do, _did, dln) in zip(rc, dc):
                want = dln + len(blk) if rid == TEXT_CHUNK_ID and (ro, rid) == (rc[-1][0], rc[-1][1]) else dln
                if rln != want:
                    problems.append('A4 chain: chunk id=%d len %d, expected %d'
                                    % (rid, rln, want))

    # A3 - the donor's own text is preserved verbatim, appended to
    if rig[d_pay:d_pay + d_len] != donor[d_pay:d_pay + d_len]:
        problems.append("A3 text: the donor's own text chunk was rewritten, not appended to")

    # A1 - the appended bytes ARE the exemplar's block, byte for byte
    got = rig[d_pay + d_len:]
    if got != blk:
        problems.append('A1 block: appended bytes are not byte-identical to %s\'s own '
                        'final CreateEntity block\n      got  %r\n      want %r'
                        % (EXEMPLAR_MESH, got[:120], blk[:120]))

    # A7 - the donor must carry no FX of its own (the block we add is the only one)
    if mesh_assets.embedded_fx_attachments_of(donor):
        problems.append('A7 donor: %s already carries embedded FX %r - it is no longer '
                        'the FX-free rig R-102 chose'
                        % (DONOR_MESH, mesh_assets.embedded_fx_attachments_of(donor)))

    # A1b - and the rig now emits exactly the exemplar's one effect, at its attach
    fx = mesh_assets.embedded_fx_attachments_of(rig)
    ex_fx = mesh_assets.embedded_fx_attachments_of(exemplar)
    if fx != ex_fx:
        problems.append('A1b fx: rig emits %r, exemplar emits %r' % (fx, ex_fx))
    if len(fx) != 1 or fx[0][0] != DEMON_ATTACH or \
            str(fx[0][1] or '').replace('/', '\\').lower() != DEMON_FX_REF.lower():
        problems.append('A1c fx: rig emits %r, expected exactly one %s at %s'
                        % (fx, DEMON_FX_REF, DEMON_ATTACH))

    # A5 - the rig (bones + attach points) is IDENTICAL: animations are safe
    dn, rn = mesh_assets.rig_names_of(donor), mesh_assets.rig_names_of(rig)
    if [n.lower() for n in dn] != [n.lower() for n in rn]:
        problems.append('A5 rig names: %d donor names vs %d rig names - the animation '
                        'surface moved (missing %r / added %r)'
                        % (len(dn), len(rn),
                           sorted(set(map(str.lower, dn)) - set(map(str.lower, rn))),
                           sorted(set(map(str.lower, rn)) - set(map(str.lower, dn)))))

    # A6 - the attach point is declared on this rig
    if DEMON_ATTACH.lower() not in {n.lower() for n in rn}:
        problems.append('A6 attach: %r is not declared on %s, so the block would hang '
                        'the smoke on nothing' % (DEMON_ATTACH, DONOR_MESH))

    # A9 - MESH-INTERNAL RENDER CLOSURE is untouched (the build30/D5 lesson).
    # `validate_render_chain` opens every soul-summoned pet's mesh and resolves the
    # shaders and textures it EMBEDS; a rig whose internal refs moved would spawn
    # an invisible or textureless pet - resolution is not rendering. Because the rig
    # is `donor || block` byte for byte, its embedded ref set can only differ by
    # what the block itself names, and this states that rather than assuming it.
    if sorted(_embedded_refs(rig)) != sorted(_embedded_refs(donor) + _embedded_refs(blk)):
        problems.append('A9 render closure: the rig embeds %r, the donor %r - the '
                        'mesh-internal shader/texture closure moved, so the wearer '
                        'could render invisible or untextured'
                        % (sorted(_embedded_refs(rig))[:8], sorted(_embedded_refs(donor))[:8]))
    return problems


def rig_bytes_checked():
    """The rig, built and fully verified, or SystemExit."""
    rig, donor, exemplar = build()
    probs = verify_rig(rig, donor, exemplar)
    if probs:
        raise RigError('[build_shroud_rig] the derived rig FAILED its own gate:\n  - '
                       + '\n  - '.join(probs))
    return rig


# ── staging ─────────────────────────────────────────────────────────────────

def entry_in(arc):
    """The rig's bytes inside an already-loaded ArcArchive, or None."""
    for e in arc.entries:
        if getattr(e, 'entry_type', 3) == 3 and \
                e.name.lower().replace('\\', '/') == SHROUD_RIG_ENTRY:
            return arc.get_file(e.name)
    return None


def add_to_arc(arc):
    """Put the verified rig into an open mod Creatures.arc. Returns its size."""
    rig = rig_bytes_checked()
    arc.add_file(SHROUD_RIG_ENTRY, rig)
    return len(rig)


# ── selftest / negtest ──────────────────────────────────────────────────────

def _selftest():
    """Re-measure every load-bearing fact against the real binaries."""
    print('=== build_shroud_rig --selftest ===')
    ok = True
    donor = read_base(DONOR_MESH)
    exemplar = read_base(EXEMPLAR_MESH)
    for label, data in (('donor   ' + DONOR_MESH, donor),
                        ('exemplar ' + EXEMPLAR_MESH, exemplar)):
        cs = chunks(data)
        last = cs[-1]
        print('  %-70s %8d B  %d chunks, last id=%d len=%d  -> EOF-exact'
              % (label, len(data), len(cs), last[1], last[2]))
        if last[1] != TEXT_CHUNK_ID:
            print('    FAIL: last chunk is not the text chunk'); ok = False
        # no other u32 in the file may equal the text-chunk length or the file size
        tl, fl, dupes = last[2], len(data), []
        for i in range(0, len(data) - 4):
            (v,) = struct.unpack_from('<I', data, i)
            if v in (tl, fl):
                dupes.append(i)
        if dupes != [last[0] + 4]:
            print('    FAIL: length/size value occurs at %r, expected only the chunk '
                  'header at %d' % (dupes, last[0] + 4)); ok = False
        else:
            print('       the only u32 equal to the text length is the chunk header itself')
    blk = exemplar_block(exemplar)
    print('  exemplar block: %d bytes  %r' % (len(blk), blk[:64]))
    print('  attach=%r entity=%r' % mesh_assets.embedded_fx_attachments_of(exemplar)[-1])
    if mesh_assets.embedded_fx_attachments_of(donor):
        print('    FAIL: the donor is not FX-free'); ok = False
    else:
        print('  donor embedded FX: NONE (as R-102 measured)')
    names = {n.lower() for n in mesh_assets.rig_names_of(donor)}
    print('  donor rig names: %d; %s declared: %s'
          % (len(names), DEMON_ATTACH, DEMON_ATTACH.lower() in names))
    if DEMON_ATTACH.lower() not in names:
        ok = False
    rig = derive(donor, exemplar)
    probs = verify_rig(rig, donor, exemplar)
    print('  derived rig: %d bytes, verify -> %s' % (len(rig), probs or 'PASS'))
    if probs:
        ok = False
    print('=== selftest %s ===' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


def _negtest():
    """Every planted corruption of the rig must be CAUGHT by verify_rig()."""
    print('=== build_shroud_rig --negtest ===')
    donor = read_base(DONOR_MESH)
    exemplar = read_base(EXEMPLAR_MESH)
    good = derive(donor, exemplar)
    if verify_rig(good, donor, exemplar):
        print('SETUP FAIL: the clean rig does not pass its own gate'); return 1

    d_hdr, d_pay, d_len = text_chunk(donor)
    blk = exemplar_block(exemplar)
    plants = []

    # P1 the b93/b99 shape of this defect: the block never gets appended at all
    plants.append(('P1 block absent (the rig is just the donor)', bytes(donor)))
    # P2 the block appended but the length u32 NOT bumped (the trap this format has)
    p2 = bytearray(donor); p2.extend(blk)
    plants.append(('P2 length u32 not bumped', bytes(p2)))
    # P3 length bumped but the block not appended
    p3 = bytearray(donor)
    p3[d_hdr + 4:d_hdr + 8] = struct.pack('<I', d_len + len(blk))
    plants.append(('P3 length bumped, no block', bytes(p3)))
    # P4 a HAND-TYPED block instead of the exemplar's own bytes (LF not CRLF)
    p4 = bytearray(donor)
    hand = blk.replace(b'\r\n', b'\n')
    p4[d_hdr + 4:d_hdr + 8] = struct.pack('<I', d_len + len(hand))
    p4.extend(hand)
    plants.append(('P4 hand-typed block (LF, not the exemplar bytes)', bytes(p4)))
    # P5 the wrong attach point - `Smoke02`, which the demons have and he does not
    p5 = bytearray(donor)
    wrong = blk.replace(b'SpecialHit01', b'Smoke02\x20\x20\x20\x20\x20')
    p5[d_hdr + 4:d_hdr + 8] = struct.pack('<I', d_len + len(wrong))
    p5.extend(wrong)
    plants.append(('P5 wrong attach point (Smoke02)', bytes(p5)))
    # P6 the wrong effect (the R-10 green-rendering one)
    p6 = bytearray(donor)
    grn = blk.replace(b'ShadowStalker_Smoke.dbr', b'RevenantPoison_FX.dbr\x20\x20')
    p6[d_hdr + 4:d_hdr + 8] = struct.pack('<I', d_len + len(grn))
    p6.extend(grn)
    plants.append(('P6 wrong effect (the R-102 green)', bytes(p6)))
    # P7 the donor's own text chunk rewritten rather than appended to
    p7 = bytearray(good)
    p7[d_pay:d_pay + 20] = b'X' * 20
    plants.append(('P7 donor text chunk overwritten', bytes(p7)))
    # P8 a byte changed BEFORE the text chunk (the geometry/skin half)
    p8 = bytearray(good)
    p8[d_hdr // 2] ^= 0xFF
    plants.append(('P8 pre-text byte corrupted', bytes(p8)))
    # P9 the block appended TWICE (a doubled shroud - denser than the demons')
    p9 = bytearray(donor)
    p9[d_hdr + 4:d_hdr + 8] = struct.pack('<I', d_len + 2 * len(blk))
    p9.extend(blk); p9.extend(blk)
    plants.append(('P9 block appended twice', bytes(p9)))
    # P10 length bumped by the WRONG amount (chain no longer walks to EOF)
    p10 = bytearray(good)
    p10[d_hdr + 4:d_hdr + 8] = struct.pack('<I', d_len + len(blk) - 1)
    plants.append(('P10 length off by one', bytes(p10)))

    caught = 0
    for label, data in plants:
        try:
            probs = verify_rig(data, donor, exemplar)
        except RigError as e:
            probs = [str(e)]
        if probs:
            caught += 1
            print('  CAUGHT  %-52s %s' % (label, probs[0].split('\n')[0][:88]))
        else:
            print('  MISSED  %-52s <<< the gate did not see this' % label)
    print('=== negtest: %d/%d plants caught ===' % (caught, len(plants)))
    return 0 if caught == len(plants) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', help='write the derived rig to this path')
    ap.add_argument('--check', action='store_true', help='derive + verify, write nothing')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--negtest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.negtest:
        return _negtest()
    rig = rig_bytes_checked()
    print('[build_shroud_rig] %s  %d bytes  (donor + the exemplar block, verified)'
          % (SHROUD_RIG, len(rig)))
    if a.out:
        p = Path(a.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(rig)
        print('[build_shroud_rig] wrote %s' % p)
    elif not a.check:
        print('[build_shroud_rig] (nothing written - pass --out or --check)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
