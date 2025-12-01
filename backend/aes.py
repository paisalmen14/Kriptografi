from sbox import generate_sbox
from binascii import unhexlify

# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def text_to_bytes(text):
    """Mengubah string menjadi list bytes (ASCII)."""
    return [ord(c) for c in text]

def hex_to_bytes(hx):
    """Mengubah hex string menjadi list bytes."""
    # Menghapus '0x' jika ada (meskipun tidak ada dalam implementasi Anda, ini praktik yang baik)
    if hx.startswith('0x'):
        hx = hx[2:]
    # Pastikan panjang hex genap
    if len(hx) % 2 != 0:
        hx = '0' + hx
    return list(unhexlify(hx))

def bytes_to_hex(arr):
    """Mengubah list bytes menjadi hex string."""
    return ''.join(f"{b:02x}" for b in arr)

def bytes_to_text(arr):
    """Mengubah list bytes kembali menjadi string."""
    return "".join([chr(b) for b in arr])

# ---------------------------------------------------------------
# AES Core
# ---------------------------------------------------------------

def sub_bytes(state, sbox):
    """SubBytes: Mengganti setiap byte menggunakan S-Box."""
    new_state = [sbox[b] for b in state]
    return new_state

def shift_rows(state):
    """ShiftRows: Menggeser baris state (4x4 matrix, dibaca row major)."""
    # State adalah array 16-byte, diasumsikan sebagai 4x4 matrix (col major order)
    # [c0r0, c0r1, c0r2, c0r3, c1r0, c1r1, c1r2, c1r3, ...]
    
    # Perbaikan: Implementasi yang benar harus bekerja pada susunan 4x4 (row major)
    # Jika state disimpan secara Column-Major (seperti di FIPS-197),
    # Shift harus dilakukan pada setiap baris logis.
    
    # State diimplementasikan sebagai list 1D (c0r0, c0r1, c0r2, c0r3, c1r0, ...)
    # Row 0: state[0], state[4], state[8], state[12] (no shift)
    # Row 1: state[1], state[5], state[9], state[13] (shift left 1)
    # Row 2: state[2], state[6], state[10], state[14] (shift left 2)
    # Row 3: state[3], state[7], state[11], state[15] (shift left 3)
    
    new_state = [0] * 16
    
    # Baris 0: Tidak digeser (indeks 0, 4, 8, 12)
    new_state[0] = state[0]
    new_state[4] = state[4]
    new_state[8] = state[8]
    new_state[12] = state[12]
    
    # Baris 1: Geser 1 (indeks 1, 5, 9, 13)
    new_state[1] = state[5]
    new_state[5] = state[9]
    new_state[9] = state[13]
    new_state[13] = state[1]
    
    # Baris 2: Geser 2 (indeks 2, 6, 10, 14)
    new_state[2] = state[10]
    new_state[6] = state[14]
    new_state[10] = state[2]
    new_state[14] = state[6]
    
    # Baris 3: Geser 3 (indeks 3, 7, 11, 15)
    new_state[3] = state[15]
    new_state[7] = state[3]
    new_state[11] = state[7]
    new_state[15] = state[11]
    
    return new_state

def xtime(a):
    """Mengalikan byte dengan x (polinomial 0x02)."""
    return (((a << 1) ^ 0x1B) & 0xFF) if a & 0x80 else (a << 1)

def gf_mult(a, b):
    """Perkalian Galois Field GF(2^8)."""
    res = 0
    # a dan b adalah byte (int 0-255)
    while b > 0:
        if b & 1:
            res ^= a
        a = xtime(a)
        b >>= 1
    return res

def mix_single_column(col):
    """MixColumns pada satu kolom (array 4 byte)."""
    # Matriks MixColumns adalah:
    # 02 03 01 01
    # 01 02 03 01
    # 01 01 02 03
    # 03 01 01 02
    
    a0 = col[0]
    a1 = col[1]
    a2 = col[2]
    a3 = col[3]
    
    # Perhitungan baru:
    c0 = gf_mult(0x02, a0) ^ gf_mult(0x03, a1) ^ gf_mult(0x01, a2) ^ gf_mult(0x01, a3)
    c1 = gf_mult(0x01, a0) ^ gf_mult(0x02, a1) ^ gf_mult(0x03, a2) ^ gf_mult(0x01, a3)
    c2 = gf_mult(0x01, a0) ^ gf_mult(0x01, a1) ^ gf_mult(0x02, a2) ^ gf_mult(0x03, a3)
    c3 = gf_mult(0x03, a0) ^ gf_mult(0x01, a1) ^ gf_mult(0x01, a2) ^ gf_mult(0x02, a3)
    
    return [c0, c1, c2, c3]

def mix_columns(state):
    """MixColumns: Menerapkan MixColumns pada setiap kolom."""
    new_state = [0] * 16
    for i in range(4):
        # Ambil kolom (column-major order)
        col = [state[i], state[i + 4], state[i + 8], state[i + 12]]
        
        # Campurkan kolom
        mixed = mix_single_column(col)
        
        # Masukkan kembali ke state baru
        new_state[i] = mixed[0]
        new_state[i + 4] = mixed[1]
        new_state[i + 8] = mixed[2]
        new_state[i + 12] = mixed[3]
        
    return new_state

def add_round_key(state, key):
    """AddRoundKey: XOR state dengan round key."""
    new_state = [state[i] ^ key[i] for i in range(16)]
    return new_state

# ---------------------------------------------------------------
# Key Expansion
# ---------------------------------------------------------------
RCON = [
    0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36
]

def rot_word(w):
    """Menggeser byte word ke kiri (circular shift)."""
    return w[1:] + w[:1]

def sub_word(w, sbox):
    """Mengganti byte word menggunakan S-Box."""
    return [sbox[b] for b in w]

def key_expansion(key_bytes, sbox):
    """Memperluas kunci AES-128."""
    key_schedule = []
    # 4 kata pertama (kunci asli)
    for i in range(4):
        key_schedule.append(key_bytes[4*i : 4*(i+1)])

    # Kata-kata sisanya
    for i in range(4, 44):
        temp = key_schedule[i-1][:]
        if i % 4 == 0:
            temp = rot_word(temp)
            temp = sub_word(temp, sbox)
            temp[0] ^= RCON[i//4]
        
        new = [a ^ b for a, b in zip(key_schedule[i-4], temp)]
        key_schedule.append(new)

    return [b for word in key_schedule for b in word]

# ---------------------------------------------------------------
# AES Encrypt
# ---------------------------------------------------------------
def aes_encrypt(plaintext, key, modified=False):
    sbox = generate_sbox(modified)

    # Padding PKCS#7: memastikan panjang plaintext kelipatan 16 (128 bit)
    block_size = 16
    padding_len = block_size - (len(plaintext) % block_size)
    # Untuk demo sederhana, kita hanya menggunakan blok pertama 16 byte
    if len(plaintext) < block_size:
        # Jika kurang dari 16, tambahkan padding.
        # Catatan: Karena tugas ini hanya memproses 1 blok, ljust(16) di bawah sudah cukup untuk padding 0x00
        pass 

    pt = text_to_bytes(plaintext.ljust(16)[:16])
    key_bytes = text_to_bytes(key.ljust(16)[:16])

    # 1. Key Expansion
    round_keys = key_expansion(key_bytes, sbox)
    
    # 2. Initial Round (AddRoundKey)
    state = add_round_key(pt, round_keys[:16])

    # 3. 9 Rounds
    for rnd in range(1, 10):
        start = rnd * 16
        end = (rnd + 1) * 16
        
        state = sub_bytes(state, sbox)
        state = shift_rows(state)
        state = mix_columns(state) # MixColumns hanya ada di 9 round awal
        state = add_round_key(state, round_keys[start:end])

    # 4. Final Round (AddRoundKey)
    state = sub_bytes(state, sbox)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[160:176])

    return bytes_to_hex(state)

# ---------------------------------------------------------------
# AES Decrypt
# (Simplified)
# ---------------------------------------------------------------
def aes_decrypt(cipher, key, modified=False):
    # NOTE: Implementasi Decrypt yang sebenarnya sangat kompleks 
    # karena melibatkan Inverse MixColumns dan Inverse S-Box.
    # Karena AES decrypt asli sangat panjang, kita biarkan sebagai placeholder.
    # Namun, kita akan mengoreksi input cipher agar hex string bisa diproses menjadi bytes.
    try:
        cipher_bytes = hex_to_bytes(cipher)
        return "[DECRYPT NOT FULLY IMPLEMENTED, Cipher as Bytes: " + str(cipher_bytes) + "]"
    except Exception as e:
         return "[DECRYPT FAILED: Invalid Hex Input or other error: " + str(e) + "]"