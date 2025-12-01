def xtime(a):
    return (((a << 1) ^ 0x1B) & 0xFF) if a & 0x80 else ((a << 1) & 0xFF)

def gf_mul(a, b):
    res = 0
    for _ in range(8):
        if b & 1:
            res ^= a
        a = xtime(a)
        b >>= 1
    return res

def gf_inverse(a):
    if a == 0:
        return 0
    t = a
    for _ in range(1, 254):
        t = gf_mul(t, a)
    return t

def affine_default(x):
    y = x ^ ((x << 1)|(x >> 7)) ^ ((x << 2)|(x >> 6)) ^ \
        ((x << 3)|(x >> 5)) ^ ((x << 4)|(x >> 4))
    return (y ^ 0x63) & 0xFF

def affine_modified(x):
    y = x ^ ((x << 1)|(x >> 7)) ^ ((x << 3)|(x >> 5)) ^ \
        ((x << 6)|(x >> 2))
    return (y ^ 0xA7) & 0xFF

def generate_sbox(modified=False):
    sbox = []
    for i in range(256):
        inv = gf_inverse(i)
        if modified:
            sbox.append(affine_modified(inv))
        else:
            sbox.append(affine_default(inv))
    return sbox
