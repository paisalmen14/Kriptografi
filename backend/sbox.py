def xtime(a):
    """Mengalikan byte dengan x (polinomial 0x02) di GF(2^8)."""
    return (((a << 1) ^ 0x1B) & 0xFF) if a & 0x80 else ((a << 1) & 0xFF)

def gf_mul(a, b):
    """Perkalian Galois Field GF(2^8)."""
    res = 0
    # a dan b adalah byte (int 0-255)
    for _ in range(8):
        if b & 1:
            res ^= a
        a = xtime(a)
        b >>= 1
    return res

def gf_inverse(a):
    """Menghitung invers di GF(2^8)."""
    if a == 0:
        return 0
    t = a
    for _ in range(1, 254):
        t = gf_mul(t, a)
    return t

def affine_default(x):
    """Transformasi Affine Standar AES."""
    y = x ^ ((x << 1)|(x >> 7)) ^ ((x << 2)|(x >> 6)) ^ \
        ((x << 3)|(x >> 5)) ^ ((x << 4)|(x >> 4))
    return (y ^ 0x63) & 0xFF

def affine_modified(x):
    """Transformasi Affine Modifikasi (S-Box custom)."""
    y = x ^ ((x << 1)|(x >> 7)) ^ ((x << 3)|(x >> 5)) ^ \
        ((x << 6)|(x >> 2))
    return (y ^ 0xA7) & 0xFF

def generate_sbox(modified=False):
    """Menghasilkan S-Box standar atau modifikasi."""
    sbox = []
    for i in range(256):
        inv = gf_inverse(i)
        if modified:
            sbox.append(affine_modified(inv))
        else:
            sbox.append(affine_default(inv))
    return sbox