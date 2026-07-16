"""tex_decode - decode Titan Quest `.tex` textures to RGBA (pure Python + numpy).

TQ `.tex` layout (reverse-engineered against the base-game InGameUI.arc, 2026-07-14):

    [3]  b"TEX"
    [1]  version byte (0x01 for small icons, 0x02 for large panes)
    [4]  flags/reserved (observed 0x00000000)
    [1]  version-2 only: one extra byte (observed 0x01) - see note
    [4]  payload size (little-endian) = len(file) - header_len
    [.]  payload = a DDS: 4-byte magic (bytes "DDS" + one trailing byte, NOT the
         standard 0x20 space) then a standard 124-byte DDS_HEADER then pixel data.

Rather than hard-code the (version-dependent) header length, the payload/DDS start
is located by searching for the DDS signature: b"DDS" immediately followed, 4 bytes
later, by the DDS_HEADER dwSize field == 124. Robust across both versions.

The skill-tree UI textures (backgrounds, connector bars, mastery panels) are all
UNCOMPRESSED 32-bit BGRA with no mipmaps (DDPF flags 0x40, bitcount 32, dwFourCC 0,
RGB masks left blank -> assume DirectX A8R8G8B8 = little-endian BGRA in memory).
Proven by exact size math, e.g. WarfareSkillBackground01: 919*540*4 == payload-128.

DXT/BC compressed `.tex` are out of scope here (none are used by the skill pane);
`decode_tex` raises for non-32-bit payloads with a clear message.
"""
import struct
import sys
from pathlib import Path

import numpy as np


class TexInfo:
    __slots__ = ("width", "height", "bits", "fourcc", "pf_flags", "mip",
                 "rgba", "dds_off", "tex_version")

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def __repr__(self):
        return ("TexInfo(%dx%d bits=%d fourcc=%r mip=%d ver=%d)"
                % (self.width, self.height, self.bits, self.fourcc,
                   self.mip, self.tex_version))


def _find_dds(data: bytes) -> int:
    """Return offset of the DDS_HEADER dwSize field (start of the 124-byte header),
    i.e. 4 bytes past the (mangled) DDS magic. Raises if not found."""
    start = 0
    while True:
        i = data.find(b"DDS", start)
        if i < 0:
            raise ValueError("no DDS signature in .tex payload")
        # magic is 4 bytes; DDS_HEADER dwSize follows and must equal 124
        if len(data) >= i + 8 and struct.unpack_from("<I", data, i + 4)[0] == 124:
            return i + 4
        start = i + 1


def decode_tex(data: bytes) -> TexInfo:
    """Decode raw `.tex` bytes -> TexInfo with an (H,W,4) uint8 RGBA array."""
    tex_version = data[3] if data[:3] == b"TEX" else -1
    hdr = _find_dds(data)                      # offset of DDS_HEADER (dwSize)
    height = struct.unpack_from("<I", data, hdr + 8)[0]
    width = struct.unpack_from("<I", data, hdr + 12)[0]
    mip = struct.unpack_from("<I", data, hdr + 24)[0]
    pf_flags = struct.unpack_from("<I", data, hdr + 76)[0]
    fourcc = data[hdr + 80:hdr + 84]
    bits = struct.unpack_from("<I", data, hdr + 84)[0]
    rmask = struct.unpack_from("<I", data, hdr + 88)[0]
    px_off = hdr + 124
    px = data[px_off:]

    if bits != 32:
        raise ValueError(
            "tex_decode: unsupported non-32-bit payload (bits=%d fourcc=%r); "
            "only uncompressed 32-bit BGRA is decoded here" % (bits, fourcc))
    need = width * height * 4
    if len(px) < need:
        raise ValueError("tex_decode: truncated pixel data (%d < %d)" % (len(px), need))
    buf = np.frombuffer(px[:need], dtype=np.uint8).reshape(height, width, 4)
    out = np.empty((height, width, 4), np.uint8)
    if rmask == 0x00FF0000 or rmask == 0:
        # DirectX A8R8G8B8: memory order B,G,R,A -> RGBA
        out[..., 0] = buf[..., 2]
        out[..., 1] = buf[..., 1]
        out[..., 2] = buf[..., 0]
        out[..., 3] = buf[..., 3]
    else:
        # explicit masks say straight RGBA
        out[:] = buf
    return TexInfo(width=width, height=height, bits=bits, fourcc=fourcc,
                   pf_flags=pf_flags, mip=mip, rgba=out, dds_off=hdr,
                   tex_version=tex_version)


def decode_arc_tex(arc, inner_name: str) -> TexInfo:
    """Decode a `.tex` stored in an already-loaded ArcArchive."""
    data = arc.get_file(inner_name)
    if data is None:
        raise FileNotFoundError("%s not in arc" % inner_name)
    return decode_tex(data)


def _main(argv):
    sys.path.insert(0, str(Path(__file__).parent))
    from arc_patcher import ArcArchive
    if len(argv) < 3:
        print("usage: py tools/tex_decode.py <arc> <inner/path.tex> [out.png]")
        return 2
    arc = ArcArchive.from_file(Path(argv[1]))
    info = decode_arc_tex(arc, argv[2])
    print(info)
    if len(argv) > 3:
        from PIL import Image
        Image.fromarray(info.rgba, "RGBA").save(argv[3])
        print("wrote", argv[3])
    return 0


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv))
