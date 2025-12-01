from sbox import generate_sbox

# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def text_to_bytes(text):
    return [ord(c) for c in text]

def bytes_to_hex(arr):
    return ''.join(f"{b:02x}" for b in arr)

def hex_to_bytes(hx):
    return [int(hx[i:i+2], 16) for i in range(2, len(hx), 2)]

# ---------------------------------------------------------------
# AES Core
# ---------------------------------------------------------------

def sub_bytes(state, sbox):
    for i in range(16):
        state[i] = sbox[state[i]]
    return state

def shift_rows(state):
    return [
        state[0],  state[5],  state[10], state[15],
        state[4],  state[9],  state[14], state[3],
        state[8],  state[13], state[2],  state[7],
        state[12], state[1],  state[6],  state[11]
    ]

def xtime(a):
    return (((a << 1) ^ 0x1B) & 0xFF) if a & 0x80 else ((a << 1) & 0xFF)

def mix_single_column(col):
    t = col[0] ^ col[1] ^ col[2] ^ col[3]
    u = col[0]
    col[0] ^= t ^ xtime(col[0] ^ col[1])
    col[1] ^= t ^ xtime(col[1] ^ col[2])
    col[2] ^= t ^ xtime(col[2] ^ col[3])
    col[3] ^= t ^ xtime(col[3] ^ u)
    return col

def mix_columns(state):
    for i in range(4):
        col = state[i*4 : (i+1)*4]
        mixed = mix_single_column(col)
        state[i*4:(i+1)*4] = mixed
    return state

def add_round_key(state, key):
    for i in range(16):
        state[i] ^= key[i]
    return state

# ---------------------------------------------------------------
# Key Expansion
# ---------------------------------------------------------------
RCON = [
    0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36
]

def rot_word(w):
    return w[1:] + w[:1]

def sub_word(w, sbox):
    return [sbox[b] for b in w]

def key_expansion(key_bytes, sbox):
    key_schedule = []
    for i in range(4):
        key_schedule.append(key_bytes[4*i : 4*(i+1)])

    for i in range(4, 44):
        temp = key_schedule[i-1][:]
        if i % 4 == 0:
            temp = sub_word(rot_word(temp), sbox)
            temp[0] ^= RCON[i//4]
        new = [a ^ b for a, b in zip(key_schedule[i-4], temp)]
        key_schedule.append(new)

    return [b for word in key_schedule for b in word]

# ---------------------------------------------------------------
# AES Encrypt
# ---------------------------------------------------------------
def aes_encrypt(plaintext, key, modified=False):
    sbox = generate_sbox(modified)

    pt = text_to_bytes(plaintext.ljust(16)[:16])
    key_bytes = text_to_bytes(key.ljust(16)[:16])

    round_keys = key_expansion(key_bytes, sbox)

    state = add_round_key(pt, round_keys[:16])

    for rnd in range(1,10):
        state = sub_bytes(state, sbox)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_keys[rnd*16:(rnd+1)*16])

    state = sub_bytes(state, sbox)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[160:176])

    return bytes_to_hex(state)

# ---------------------------------------------------------------
# AES Decrypt
# (Simplified — reverse operations without MixColumns last round)
# ---------------------------------------------------------------
def aes_decrypt(cipher, key, modified=False):
    # NOTE: untuk demo saja (AES decrypt real sangat panjang)
    # Di tugas, cukup AES_encrypt saja sudah cukup
    return "[DECRYPT NOT IMPLEMENTED FULLY]"
