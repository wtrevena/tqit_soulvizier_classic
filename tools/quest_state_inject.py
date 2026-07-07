"""Character-copy + quest-registration tool for TQAE custom-quest saves.

Built for the Widow-Letter investigation (2026-07-06). See
docs/QUEST_STATE_INJECT.md for the full format findings, evidence, and why
quest-registration injection is a NO-OP for the current letter bug (the four
July SV quests fail to LOAD world-side; the per-character save is not the
gate). The COPY workflow is the useful part: it clones Will's character into a
sandbox slot (default `_ToxeuQ`) with items/level/skills/spawn/waypoints/
fog-of-war all preserved, so anything risky can be tested without touching
`_Toxeus`.

SAFETY CONTRACT
===============
- NEVER writes inside the source character folder. Every write goes to the
  copy folder (or the backup zip under local/save_backups/).
- Re-runnable: each run deletes and re-creates the COPY folder from the
  current on-disk state of the source (run it right after Will saves+exits to
  refresh the sandbox).
- After every run it re-hashes the source tree and compares against the
  pre-run manifest: any drift aborts with a loud error.

USAGE
=====
  python tools/quest_state_inject.py --copy                # backup + copy + rename
  python tools/quest_state_inject.py --copy --inject widowletter urder \
        bossarena open_bloodcave_portal                    # + Quest.myw entries (see doc: currently ineffective)
  python tools/quest_state_inject.py --verify-only         # just check the original against the backup manifest

FORMAT KNOWLEDGE (reverse-engineered, evidence in docs/QUEST_STATE_INJECT.md)
=============================================================================
- Quest identity: md5(b"quests\\<basename>.qst") over the lowercase,
  backslash-separated registration path. The 16-byte digest is stored as four
  little-endian u32 `md5Chunk` values in Quest.myw; the per-quest state file
  is named "%08x%08x%08x%08x.que" % those four u32s.
- Quest.myw = one `begin_block numberOfTriggers=N` list of ARMED-TRIGGER
  entries {questName(hashed) stepIdx triggerIdx target} + a trailing
  `numRewards` block (pending journal rewards). Byte-exact round-trip
  verified against Will's live file (124 entries + 530-byte tail).
- .que files are created LAZILY by the engine the first time a quest's state
  differs from default. Absence of a .que = virgin state, NOT "not tracked".
  Therefore no .que synthesis is needed (or wise) when registering a quest.
"""
import argparse
import hashlib
import json
import shutil
import struct
import sys
import zipfile
from datetime import date
from pathlib import Path

BEGIN = 0xB01DFACE
END = 0xDEADC0DE
BS = '\\'

DEFAULT_SOURCE = Path(r"C:\Users\willi\OneDrive\Documents\My Games"
                      r"\Titan Quest - Immortal Throne\SaveData\User\_Toxeus")
DEFAULT_MAP_SUBDIR = Path("Levels_world_world01.map") / "Normal"
BACKUP_DIR = Path(__file__).resolve().parent.parent / "local" / "save_backups"


# ----------------------------------------------------------------------------
# identity hashing (cracked scheme)
# ----------------------------------------------------------------------------
def quest_identity_chunks(basename: str):
    """4 little-endian u32 md5 chunks for a quest registered as Quests/<basename>."""
    path = ("quests" + BS + basename).lower()
    d = hashlib.md5(path.encode('utf-8')).digest()
    return list(struct.unpack('<4I', d))


def chunks_to_que_filename(chunks):
    return ''.join(struct.pack('<I', c)[::-1].hex() for c in chunks) + '.que'


# ----------------------------------------------------------------------------
# Quest.myw parser / serializer (byte-exact round-trip)
# ----------------------------------------------------------------------------
class _Reader:
    def __init__(self, b):
        self.b = b
        self.o = 0

    def u32(self):
        v = struct.unpack_from('<I', self.b, self.o)[0]
        self.o += 4
        return v

    def key(self):
        n = self.u32()
        s = self.b[self.o:self.o + n].decode('ascii')
        self.o += n
        return s

    def peek_key(self):
        save = self.o
        try:
            k = self.key()
        except Exception:
            self.o = save
            return None
        self.o = save
        return k


def parse_quest_myw(b):
    r = _Reader(b)
    assert r.key() == 'begin_block' and r.u32() == BEGIN
    assert r.key() == 'numberOfTriggers'
    count = r.u32()
    entries = []
    for _ in range(count):
        assert r.key() == 'questName'
        assert r.key() == 'md5ChunkCount'
        cc = r.u32()
        chunks = []
        for _ in range(cc):
            assert r.key() == 'md5Chunk'
            chunks.append(r.u32())
        assert r.key() == 'stepIdx'
        step = r.u32()
        assert r.key() == 'triggerIdx'
        trig = r.u32()
        assert r.key() == 'target'
        if r.peek_key() == 'md5ChunkCount':
            r.key()
            tc = r.u32()
            tchunks = []
            for _ in range(tc):
                assert r.key() == 'md5Chunk'
                tchunks.append(r.u32())
            target = ('hashed', tchunks)
        else:
            target = ('u32', r.u32())
        entries.append({'chunks': chunks, 'stepIdx': step,
                        'triggerIdx': trig, 'target': target})
    assert r.key() == 'end_block' and r.u32() == END
    return entries, b[r.o:]


def _k(s):
    bb = s.encode('ascii')
    return struct.pack('<I', len(bb)) + bb


def build_quest_myw(entries, tail=b''):
    out = bytearray()
    out += _k('begin_block') + struct.pack('<I', BEGIN)
    out += _k('numberOfTriggers') + struct.pack('<I', len(entries))
    for e in entries:
        out += _k('questName')
        out += _k('md5ChunkCount') + struct.pack('<I', len(e['chunks']))
        for c in e['chunks']:
            out += _k('md5Chunk') + struct.pack('<I', c)
        out += _k('stepIdx') + struct.pack('<I', e['stepIdx'])
        out += _k('triggerIdx') + struct.pack('<I', e['triggerIdx'])
        out += _k('target')
        kind, val = e['target']
        if kind == 'hashed':
            out += _k('md5ChunkCount') + struct.pack('<I', len(val))
            for c in val:
                out += _k('md5Chunk') + struct.pack('<I', c)
        else:
            out += struct.pack('<I', val)
    out += _k('end_block') + struct.pack('<I', END)
    out += tail
    return bytes(out)


# ----------------------------------------------------------------------------
# hashing / verification
# ----------------------------------------------------------------------------
def hash_tree(root: Path):
    tree = {}
    for p in sorted(root.rglob('*')):
        if p.is_file():
            data = p.read_bytes()
            tree[p.relative_to(root).as_posix()] = [len(data),
                                                    hashlib.sha256(data).hexdigest()]
    return tree


def backup_zip(src: Path, out_zip: Path, manifest: Path):
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    tree = {}
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in sorted(src.rglob('*')):
            if p.is_file():
                rel = p.relative_to(src).as_posix()
                data = p.read_bytes()
                tree[rel] = [len(data), hashlib.sha256(data).hexdigest()]
                z.writestr(f"{src.name}/{rel}", data)
    manifest.write_text(json.dumps(tree, indent=1))
    return tree


# ----------------------------------------------------------------------------
# Player.chr rename (same-length only: zero structural risk)
# ----------------------------------------------------------------------------
def patch_player_name(chr_path: Path, old_name: str, new_name: str):
    if len(new_name) != len(old_name):
        raise SystemExit(f"refusing rename: '{new_name}' must be exactly "
                         f"{len(old_name)} chars (same-length patch keeps the "
                         f"tag-stream byte-identical in size)")
    b = bytearray(chr_path.read_bytes())
    key = struct.pack('<I', len('myPlayerName')) + b'myPlayerName'
    p = b.find(key)
    if p < 0:
        raise SystemExit("myPlayerName field not found in Player.chr")
    o = p + len(key)
    n_chars = struct.unpack_from('<I', b, o)[0]
    old_bytes = old_name.encode('utf-16-le')
    if n_chars != len(old_name) or bytes(b[o + 4:o + 4 + len(old_bytes)]) != old_bytes:
        raise SystemExit(f"myPlayerName mismatch: expected {old_name!r} "
                         f"({n_chars} chars found)")
    b[o + 4:o + 4 + len(old_bytes)] = new_name.encode('utf-16-le')
    chr_path.write_bytes(bytes(b))
    return True


# ----------------------------------------------------------------------------
# quest registration injection (Quest.myw armed-trigger entries)
# ----------------------------------------------------------------------------
def inject_quests(myw_path: Path, quest_basenames, arm=((0, 0), (0, 1), (1, 0), (2, 0))):
    """Append armed-trigger entries for the given quests to the copy's Quest.myw.

    NOTE (evidence in docs/QUEST_STATE_INJECT.md): with the current deployed
    map this is a NO-OP in-game, because the four SV quests are never LOADED
    by the engine (world-side registration-slot bug). The engine also adopts
    newly-loadable quests automatically, so once the map is fixed this
    injection is unnecessary. Kept because it is harmless (unknown entries are
    dropped at next save) and documents the write path.
    """
    b = myw_path.read_bytes()
    entries, tail = parse_quest_myw(b)
    rebuilt = build_quest_myw(entries, tail)
    if rebuilt != b:
        raise SystemExit("round-trip mismatch on Quest.myw; aborting (format drift?)")
    existing = {tuple(e['chunks']) for e in entries}
    added = 0
    for bn in quest_basenames:
        if not bn.endswith('.qst'):
            bn += '.qst'
        chunks = quest_identity_chunks(bn)
        if tuple(chunks) in existing:
            print(f"  already present: {bn}")
            continue
        for step, trig in arm:
            entries.append({'chunks': chunks, 'stepIdx': step,
                            'triggerIdx': trig, 'target': ('u32', 0)})
            added += 1
        print(f"  injected {bn} -> {chunks_to_que_filename(chunks)} "
              f"({len(arm)} armed triggers)")
    out = build_quest_myw(entries, tail)
    # verify: re-parse and confirm the ORIGINAL entries survive byte-exact
    e2, t2 = parse_quest_myw(out)
    assert t2 == tail
    assert [ (tuple(x['chunks']), x['stepIdx'], x['triggerIdx'], x['target'])
             for x in e2[:len(e2) - added] ] == \
           [ (tuple(x['chunks']), x['stepIdx'], x['triggerIdx'], x['target'])
             for x in parse_quest_myw(b)[0] ]
    myw_path.write_bytes(out)
    print(f"  Quest.myw: {len(parse_quest_myw(b)[0])} -> {len(e2)} entries")


# ----------------------------------------------------------------------------
# main workflow
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    ap.add_argument('--copy-name', default='ToxeuQ',
                    help='internal+folder name for the sandbox copy '
                         '(must be same length as the source name)')
    ap.add_argument('--copy', action='store_true', help='create/refresh the copy')
    ap.add_argument('--inject', nargs='*', metavar='QUEST',
                    help='quest basenames to register in the COPY (e.g. '
                         'widowletter urder bossarena open_bloodcave_portal). '
                         'See doc: currently ineffective in-game.')
    ap.add_argument('--verify-only', action='store_true',
                    help='only verify the original against the backup manifest')
    args = ap.parse_args()

    src = args.source
    if not src.is_dir():
        raise SystemExit(f"source not found: {src}")
    src_name = src.name.lstrip('_')

    stamp = date.today().isoformat()
    zip_path = BACKUP_DIR / f"{src.name}_{stamp}.zip"
    manifest_path = BACKUP_DIR / f"{src.name}_{stamp}.hashes.json"

    # 1. pre-run hash of the ORIGINAL
    pre = hash_tree(src)

    if args.verify_only:
        if manifest_path.exists():
            saved = json.loads(manifest_path.read_text())
            same = saved == pre
            print(f"original vs {manifest_path.name}: "
                  f"{'IDENTICAL' if same else 'DIFFERS (new play session since backup?)'}")
        else:
            print("no manifest for today; current tree hashed OK "
                  f"({len(pre)} files)")
        return

    # 2. backup: skip only if today's manifest exists AND matches the current tree;
    #    never overwrite an existing zip (suffix a counter instead)
    need_backup = True
    if zip_path.exists() and manifest_path.exists():
        if json.loads(manifest_path.read_text()) == pre:
            need_backup = False
            print(f"backup up to date: {zip_path.name}")
    if need_backup:
        n = 1
        while zip_path.exists():
            zip_path = BACKUP_DIR / f"{src.name}_{stamp}_{n}.zip"
            manifest_path = BACKUP_DIR / f"{src.name}_{stamp}_{n}.hashes.json"
            n += 1
        print(f"backing up {src.name} -> {zip_path.name}")
        backup_zip(src, zip_path, manifest_path)

    if args.copy:
        dst = src.parent / f"_{args.copy_name}"
        if dst.resolve() == src.resolve():
            raise SystemExit("copy target equals source; refusing")
        if dst.exists():
            print(f"removing previous copy {dst.name}")
            shutil.rmtree(dst)
        print(f"copying {src.name} -> {dst.name}")
        shutil.copytree(src, dst)
        print("patching internal character name")
        patch_player_name(dst / 'Player.chr', src_name, args.copy_name)
        bak = dst / 'Backup' / 'Player.chr'
        if bak.exists():
            try:
                patch_player_name(bak, src_name, args.copy_name)
            except SystemExit as e:
                print(f"  (Backup/Player.chr not patched: {e})")

        if args.inject:
            myw = dst / DEFAULT_MAP_SUBDIR / 'Quest.myw'
            print(f"injecting quest registrations into {myw.relative_to(dst)}")
            inject_quests(myw, args.inject)

        print(f"copy ready: {dst}")

    # 3. post-run verification: the ORIGINAL must be untouched
    post = hash_tree(src)
    if post != pre:
        raise SystemExit("!!! ORIGINAL TREE CHANGED DURING RUN - investigate immediately !!!")
    print(f"original untouched ({len(post)} files, hash-tree identical)")


if __name__ == '__main__':
    main()
