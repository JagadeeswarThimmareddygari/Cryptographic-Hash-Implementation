#!/usr/bin/python3

import struct
from constants import *

_k = FRACTIONAL_PARTS_OF_CUBERTS_OF_PRIMES

# Mask off to 64 bit word
def mask(a):
    return ( a & 0xffffffffffffffff)

# Rotate right 64 bit
def rr(x,y):
    one = (x >> y)
    two = (x << (64-y))
    three = one | two
    return mask(three) 

# Two standard mix functions for the state expand
def f1(w):
    one = rr(w[-2], 19)
    two = rr(w[-2], 61)
    three = (w[-2] >> 6)
    res = one ^ two ^ three
    return res

def f2(w):
    one = rr(w[-15], 1)
    two = rr(w[-15], 8)
    three = (w[-15] >> 7)
    res = one ^ two ^ three
    return res

# expanding from 16 words to 80 words and returning the list of words    
def expand_state(c):
    w = list(struct.unpack('!16Q', c))
    
    for i in range(16, 80):
        mix1 = f1(w)
        mix2 = f2(w)
        three = w[-16]
        four = w[-7]
        summ = mix1 + mix2 + three + four
        res = mask(summ)
        w.append(res)
        
    return w

# sha512 inner loop operations

# rotate A from mixer 1
def s0(a):
    one = rr(a, 28)
    two = rr(a, 34)
    three = rr(a, 39)
    res = one ^ two ^ three
    return res

# rotate E from mixer 2
def s1(e):
    one = rr(e, 14)
    two = rr(e, 18)
    three = rr(e, 41)
    res = one ^ two ^ three
    return res

# majority from mixer 1
def maj(v):
    first = v[0] & v[1] 
    second = v[0] & v[2]
    third = v[1] & v[2]
    res = first | second | third
    return res

# conditional from mixer 2
def conditional(v):
    first = v[0] & v[1]
    second = ~v[0] & v[2]
    res = first | second
    return res

def mixer_one(v):
    return s0(v[0]) + maj(v)

def mixer_two(v,i,w):
    first = s1(v[4])
    second = conditional(v[4:7])
    summ = first
    summ += second
    summ += v[7]
    summ += w[i]
    summ += _k[i]
    return summ


def do_chunk(c, h):
    w = expand_state(c)
    v = h # a0:h0 = h; v = a:h

    for i in range(80):
        mix1 = mixer_one(v)
        mix2 = mixer_two(v, i, w)
        x = mask(mix1 + mix2)
        y = mask(v[3] + mix2)
        v = (x, v[0], v[1], v[2], y, v[4], v[5], v[6])

    res = [mask(x+y) for x,y in zip(h, v)] # adding a:h to initial a0:h0
    return res

# pad message, +'1' bit, then '0' bits to fit evenly mod 1024 bit w/
# 128 bit msg length at the end. Make extra chunk if it won't fit. 
def pad(m):
    # print(m, len(m))
    length_in_bits = len(m) * 8 # each utf-8 character is 8 bits
    tail = struct.pack("!Q", length_in_bits)
    tail = b"\x00" * 8 + tail # concatenation, beware b'f' and b'\x65' are the same because it's f the alphabet not f as in 15

    one = (len(m)%128)>(128-16-1)
    two = 128 if one else 0
    three = (128-16-1) + two -(len(m)%128)
    four = b"\x00" * three
    # print(two, three, four, len(four))
    padding = b"\x80"  + four
    # print(padding, len(padding))
    return m + padding + tail

def merkle_damgard(m, h):
    for i in range(0, len(m), 128):
        chunk = m[i: i + 128]
        compression_result = do_chunk(chunk, h)
        h = compression_result
    res = struct.pack("!8Q",*h)  # ! - big endian, 8 - 8 params that follow, Q - unsigned long long
    return res

def sha512(msg):
    initial_hash = FRACTIONAL_PARTS_OF_SQRTS_OF_PRIMES
    msg = pad(msg)
    res = merkle_damgard(msg, initial_hash)
    return res

    # Run some test vectors (from nist.gov, reformatted for python use)
    # The final one, 'a'*1000000, will bottom out max_recursion in most
    # setups since it does 
    #   f( rest, state) => f( rest[size:], do(rest[:size], state))
    # spawning 1e6//128 == 7.8k depth

def do_some_tests():
    tvs = [
        {"m":"abc", "r256": "ba7816bf 8f01cfea 414140de 5dae2223 b00361a3 96177a9c b410ff61 f20015ad", "r512": "ddaf35a193617aba cc417349ae204131 12e6fa4e89a97ea2 0a9eeee64b55d39a 2192992a274fc1a8 36ba3c23a3feebbd 454d4423643ce80e 2a9ac94fa54ca49f"},
        {"m": "", "r256": "e3b0c442 98fc1c14 9afbf4c8 996fb924 27ae41e4 649b934c a495991b 7852b855", "r512": "cf83e1357eefb8bd f1542850d66d8007 d620e4050b5715dc 83f4a921d36ce9ce 47d0d13c5d85f2b0 ff8318d2877eec2f 63b931bd47417a81 a538327af927da3e"}, 
        {"m": "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq", "r256": "248d6a61 d20638b8 e5c02693 0c3e6039 a33ce459 64ff2167 f6ecedd4 19db06c1", "r512": "204a8fc6dda82f0a 0ced7beb8e08a416 57c16ef468b228a8 279be331a703c335 96fd15c13b1b07f9 aa1d3bea57789ca0 31ad85c7a71dd703 54ec631238ca3445"}, 
        {"m": "abcdefghbcdefghicdefghijdefghijkefghijklfghijklmghijklmnhijklmnoijklmnopjklmnopqklmnopqrlmnopqrsmnopqrstnopqrstu", "r256": "cf5b16a7 78af8380 036ce59e 7b049237 0b249b11 e8f07a51 afac4503 7afee9d1", "r512": "8e959b75dae313da 8cf4f72814fc143f 8f7779c6eb9f7fa1 7299aeadb6889018 501d289e4900f7e4 331b99dec4b5433a c7d329eeb6dd2654 5e96e55b874be909"}, 
        {"m": "a"*1000000, "r256": "cdc76e5c 9914fb92 81a1c7e2 84d73e67 f1809a48 a497200e 046d39cc c7112cd0", "r512": "e718483d0ce76964 4e2e42c7bc15b463 8e1f98b13b204428 5632a803afa973eb de0ff244877ea60a 4cb0432ce577c31b eb009c5c2c49aa2e 4eadb217ad8cc09b"}
    ]
    # for tv in tvs[:-1]:  # Remove [:-1] to not skip recursion-killer-size case
    for tv in tvs:
        m = tv['m']
        realr = tv['r512'].replace(" ","")
        ncr = sha512(m.encode())
        calcr = (''.join("%02x"%(a) for a in ncr))
        if realr!=calcr:
            print("FAIL")
            print(realr)
            print(calcr)
            quit()
        else:
            print("PASS")
            # print(realr)
            # print(calcr)

if __name__ == '__main__':
    do_some_tests()

    # m = ''
    # ncr = sha512(m.encode())
    # calcr = (''.join("%02x"%(a) for a in ncr))
    # print(calcr)
