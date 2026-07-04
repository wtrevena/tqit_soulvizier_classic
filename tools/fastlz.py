"""Exact Python port of FastLZ 0.1.0 (fastlz.c) level 1, as bundled in
recastnavigation/RecastDemo/Contrib/fastlz. Little-endian (x86) semantics.
"""

MAX_COPY = 32
MAX_LEN = 264  # 256 + 8
MAX_DISTANCE1 = 8192
HASH_LOG = 13
HASH_SIZE = 1 << HASH_LOG
HASH_MASK = HASH_SIZE - 1


def _readu16(b, i):
    return b[i] | (b[i + 1] << 8)


def _hash(b, i):
    v = _readu16(b, i)
    v ^= _readu16(b, i + 1) ^ (v >> (16 - HASH_LOG))
    return v & HASH_MASK


def fastlz1_decompress(inp, maxout):
    ip = 0
    ip_limit = len(inp)
    out = bytearray(maxout)
    op = 0
    ctrl = inp[ip] & 31
    ip += 1
    loop = True
    while loop:
        ref = op
        length = ctrl >> 5
        ofs = (ctrl & 31) << 8
        if ctrl >= 32:
            length -= 1
            ref -= ofs
            if length == 7 - 1:
                length += inp[ip]; ip += 1
            ref -= inp[ip]; ip += 1
            if op + length + 3 > maxout:
                return None
            if ref - 1 < 0:
                return None
            if ip < ip_limit:
                ctrl = inp[ip]; ip += 1
            else:
                loop = False
            if ref == op:
                # run
                b = out[ref - 1]
                out[op] = b; out[op+1] = b; out[op+2] = b
                op += 3
                for _ in range(length):
                    out[op] = b; op += 1
            else:
                ref -= 1
                for _ in range(3 + length):
                    out[op] = out[ref]
                    op += 1; ref += 1
        else:
            ctrl += 1
            if op + ctrl > maxout:
                return None
            if ip + ctrl > ip_limit:
                return None
            out[op:op+ctrl] = inp[ip:ip+ctrl]
            op += ctrl; ip += ctrl
            loop = ip < ip_limit
            if loop:
                ctrl = inp[ip]; ip += 1
    return bytes(out[:op])


def fastlz1_compress(inp):
    length = len(inp)
    ip = 0
    ip_bound = length - 2
    ip_limit = length - 12
    op = bytearray()

    if length < 4:
        if length:
            op.append(length - 1)
            op += inp[:length]
            return bytes(op)
        return b''

    htab = [0] * HASH_SIZE

    copy = 2
    op.append(MAX_COPY - 1)
    op.append(inp[ip]); ip += 1
    op.append(inp[ip]); ip += 1

    while ip < ip_limit:
        anchor = ip
        # find potential match
        hval = _hash(inp, ip)
        ref = htab[hval]
        distance = anchor - ref
        htab[hval] = anchor

        if (distance == 0 or distance >= MAX_DISTANCE1 or
                inp[ref] != inp[ip] or inp[ref+1] != inp[ip+1] or inp[ref+2] != inp[ip+2]):
            # literal
            op.append(inp[anchor])
            ip = anchor + 1
            copy += 1
            if copy == MAX_COPY:
                copy = 0
                op.append(MAX_COPY - 1)
            continue

        ref += 3
        # last matched byte
        ip = anchor + 3
        distance -= 1
        if distance == 0:
            # zero distance means a run
            x = inp[ip - 1]
            while ip < ip_bound:
                if inp[ref] != x:
                    break
                ref += 1
                ip += 1
        else:
            while True:
                broke = False
                for _ in range(8):
                    if inp[ref] != inp[ip]:
                        broke = True
                        ref += 1; ip += 1
                        break
                    ref += 1; ip += 1
                if not broke:
                    while ip < ip_bound:
                        if inp[ref] != inp[ip]:
                            ref += 1; ip += 1
                            break
                        ref += 1; ip += 1
                break

        # adjust copy count
        if copy:
            op[len(op) - copy - 1] = copy - 1
        else:
            op.pop()
        copy = 0

        ip -= 3
        mlen = ip - anchor

        # encode the match (level 1)
        if mlen > MAX_LEN - 2:
            while mlen > MAX_LEN - 2:
                op.append((7 << 5) + (distance >> 8))
                op.append(MAX_LEN - 2 - 7 - 2)
                op.append(distance & 255)
                mlen -= MAX_LEN - 2
        if mlen < 7:
            op.append((mlen << 5) + (distance >> 8))
            op.append(distance & 255)
        else:
            op.append((7 << 5) + (distance >> 8))
            op.append(mlen - 7)
            op.append(distance & 255)

        # update hash at match boundary
        htab[_hash(inp, ip)] = ip; ip += 1
        htab[_hash(inp, ip)] = ip; ip += 1

        # assuming literal copy
        op.append(MAX_COPY - 1)

    # left-over as literal copy
    while ip <= ip_bound + 1:
        if ip >= length:
            break
        op.append(inp[ip]); ip += 1
        copy += 1
        if copy == MAX_COPY:
            copy = 0
            op.append(MAX_COPY - 1)

    if copy:
        op[len(op) - copy - 1] = copy - 1
    else:
        op.pop()

    return bytes(op)
