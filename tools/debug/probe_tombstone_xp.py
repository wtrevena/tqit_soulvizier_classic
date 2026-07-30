r"""tools/debug/probe_tombstone_xp.py - reproduce the R-109 mechanism proof.

READ-ONLY. Touches no repo file, no game file, no deploy target. It opens the
stock 32-bit `Game.dll` from the Steam TQAE install, walks the PE export
directory, and disassembles the four functions that make up the death ->
gravestone -> recovery loop, plus the GameEngine field loader that populates
`RedemptionMultiplier`.

    py tools/debug/probe_tombstone_xp.py --disasm
    py tools/debug/probe_tombstone_xp.py --strings
    py tools/debug/probe_tombstone_xp.py --disasm --dll "<path to Game.dll>"

Requires `capstone` (already used nowhere else in the build; this is a debug tool
and nothing in tools/ imports it).

WHAT IT PROVES (see tools/patches/tombstone_xp_recovery.py section 1 for the full
write-up; addresses are for image base 0x10000000):

  ?CharacterIsDying@Player@GAME@@UAEXXZ                       the on-death handler
  ?GetPlayerDeathExperiencePenalty@GameEngine@GAME@@QBEI...   clamp(equation, min, max)
  ?RegisterExperienceLoss@GameEngine@GAME@@QAEXIH@Z           stores the ACTUAL loss at GraveInfo+0x0C
  ?GetPlayerExperienceRedemptionAmount@GameEngine@GAME@@IAEII@Z
                                                              reads GraveInfo+0x0C, `mulss` by GE+0x2A04
  ?PlayerExperienceRedemption@GameEngine@GAME@@QAEXI_N@Z      the grave-touch handler

  ... and the loader site that writes GE+0x2A04 from the string
  "RedemptionMultiplier" with the engine default 0.5f (0x3f000000).

Conclusion, readable off the output: recovered = trunc(actual_lost * GE+0x2A04),
so `RedemptionMultiplier = 1.0` makes recovery EQUAL the loss, derived from the
penalty rather than hardcoded to any percentage.
"""
import struct
import sys
from pathlib import Path

DEFAULT_DLL = Path(r'C:\Program Files (x86)\Steam\steamapps\common'
                   r'\Titan Quest Anniversary Edition\Game.dll')

WANTED = (
    'CharacterIsDying',
    'GetPlayerDeathExperiencePenalty',
    'RegisterExperienceLoss',
    'GetPlayerExperienceRedemptionAmount',
    'PlayerExperienceRedemption',
    'GetMainPlayersGraveData',
)

NEEDLES = (b'RedemptionMultiplier', b'deathPenaltyEquation', b'deathPenaltyMin',
           b'deathPenaltyMax', b'FixedItemGravestone', b'GraveEffect',
           b'Records/XPack/Item/Gravestones/GravestoneGreece.dbr',
           b'Records/XPack/Game/GameEngine.dbr')


class PE32:
    def __init__(self, path):
        self.path = Path(path)
        d = self.data = self.path.read_bytes()
        e = struct.unpack_from('<I', d, 0x3c)[0]
        if d[e:e + 4] != b'PE\0\0':
            raise SystemExit('not a PE: %s' % path)
        coff = e + 4
        nsec = struct.unpack_from('<H', d, coff + 2)[0]
        opt_size = struct.unpack_from('<H', d, coff + 16)[0]
        opt = coff + 20
        if struct.unpack_from('<H', d, opt)[0] != 0x10b:
            raise SystemExit('expected a 32-bit PE')
        self.image_base = struct.unpack_from('<I', d, opt + 28)[0]
        ndir = struct.unpack_from('<I', d, opt + 92)[0]
        self.dirs = [struct.unpack_from('<II', d, opt + 96 + i * 8) for i in range(ndir)]
        st = opt + opt_size
        self.sections = []
        for i in range(nsec):
            o = st + i * 40
            nm = d[o:o + 8].rstrip(b'\0').decode('ascii', 'replace')
            vsz, va, rsz, rp = struct.unpack_from('<IIII', d, o + 8)
            self.sections.append((nm, va, vsz, rp, rsz))

    def rva2off(self, rva):
        for _nm, va, vsz, rp, rsz in self.sections:
            if va <= rva < va + max(vsz, rsz):
                return rp + (rva - va)
        return None

    def off2rva(self, off):
        for _nm, va, _vsz, rp, rsz in self.sections:
            if rp <= off < rp + rsz:
                return va + (off - rp)
        return None

    def va(self, rva):
        return self.image_base + rva

    def exports(self):
        d = self.data
        er, _sz = self.dirs[0]
        eo = self.rva2off(er)
        _nf, n_names = struct.unpack_from('<II', d, eo + 20)
        ar, nr, orr = struct.unpack_from('<III', d, eo + 28)
        ao, no, oo = self.rva2off(ar), self.rva2off(nr), self.rva2off(orr)
        out = {}
        for i in range(n_names):
            p = struct.unpack_from('<I', d, no + i * 4)[0]
            off = self.rva2off(p)
            nm = d[off:d.index(b'\0', off)].decode('ascii', 'replace')
            ordi = struct.unpack_from('<H', d, oo + i * 2)[0]
            out[nm] = struct.unpack_from('<I', d, ao + ordi * 4)[0]
        return out

    def find(self, needle):
        out, k = [], 0
        while True:
            k = self.data.find(needle, k)
            if k < 0:
                return out
            out.append(k)
            k += 1

    def xrefs_to_va(self, va):
        return self.find(struct.pack('<I', va))


def _md():
    try:
        from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    except ImportError:
        raise SystemExit('probe_tombstone_xp: capstone is required for --disasm '
                         '(py -m pip install capstone)')
    return Cs(CS_ARCH_X86, CS_MODE_32)


def disasm(pe, rva, label, maxins=140):
    md = _md()
    off = pe.rva2off(rva)
    print('\n===== %s\n      RVA 0x%08x  VA 0x%08x =====' % (label, rva, pe.va(rva)))
    n = 0
    for ins in md.disasm(pe.data[off:off + 16 * maxins], pe.va(rva)):
        print('  0x%08x  %-22s %s' % (ins.address, ins.mnemonic, ins.op_str))
        n += 1
        if ins.mnemonic.startswith('ret') or n >= maxins:
            break


def main(argv):
    dll = DEFAULT_DLL
    if '--dll' in argv:
        dll = Path(argv[argv.index('--dll') + 1])
    if not dll.exists():
        raise SystemExit('probe_tombstone_xp: Game.dll not found at %s '
                         '(pass --dll <path>)' % dll)
    pe = PE32(dll)
    print('Game.dll : %s' % dll)
    print('size     : %d bytes   image_base 0x%08x' % (len(pe.data), pe.image_base))

    if '--strings' in argv or '--disasm' not in argv:
        print('\n===== the vocabulary, in the shipped bytes =====')
        for n in NEEDLES:
            hits = pe.find(n)
            print('  %-58s %d hit(s)%s'
                  % (n.decode(), len(hits),
                     ('  first @ file 0x%08x' % hits[0]) if hits else ''))

    if '--disasm' in argv:
        exp = pe.exports()
        picked = {}
        for nm, rva in exp.items():
            for w in WANTED:
                if w in nm:
                    picked.setdefault(w, (nm, rva))
        for w in WANTED:
            if w not in picked:
                print('\n!! export not found: %s' % w)
                continue
            nm, rva = picked[w]
            disasm(pe, rva, nm)

        # the loader site that populates RedemptionMultiplier
        hits = pe.find(b'RedemptionMultiplier\0')
        if hits:
            sva = pe.va(pe.off2rva(hits[0]))
            print('\n\n===== "RedemptionMultiplier" literal VA 0x%08x =====' % sva)
            md = _md()
            for k in pe.xrefs_to_va(sva):
                lo = max(0, k - 32)
                print('  --- loader site, file 0x%08x ---' % k)
                for ins in md.disasm(pe.data[lo:k + 40], pe.va(pe.off2rva(lo))):
                    print('    0x%08x  %-22s %s'
                          % (ins.address, ins.mnemonic, ins.op_str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
